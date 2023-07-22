# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from google.cloud import bigquery
from langchain.tools.base import BaseTool
from pydantic import BaseModel, Extra, Field


class BaseBigQueryTool(BaseModel):
    """Base tool for interacting with a SQL database."""

    db: bigquery.Client = Field(exclude=True)
    dataset: str = Field(exclude=True)

    # Override BaseTool.Config to appease mypy
    # See https://github.com/pydantic/pydantic/issues/4173
    class Config(BaseTool.Config):
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True
        extra = Extra.forbid


class QueryBigQueryTool(BaseBigQueryTool, BaseTool):
    """Tool for querying a BigQuery table."""

    return_direct = False
    name = "query_bigquery"
    description = """
    Input to this tool is a detailed and correct BigQuery query, output is a result from the BigQuery table.
    If the query is not correct, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.
    """

    def _run(self, query: str) -> str:
        """Execute the query, return the results or an error message."""
        try:
            query = query.strip("'")
            job = self.db.query(query)
            rows = job.result(20)
            if rows is None:
                return "[]"
            results = []
            for row in rows:
                results.append(row)
            return f"{results}"
        except Exception as e:
            return f"[Error]{str(e)}"

    async def _arun(self, query: str) -> str:
        raise NotImplementedError("QuerySqlDbTool does not support async")


class InfoBigQueryTool(BaseBigQueryTool, BaseTool):
    """Tool for getting metadata about a SQL database."""

    name = "schema_bigquery"
    description = """
    Tool for getting metadata about a SQL database.
    Input to this tool is a comma-separated list of tables, output is the schema and sample rows for those tables.
    Be sure that the tables actually exist by calling list_tables_sql_db first!

    Example Input: "table1, table2, table3"
    """

    def _run(self, table_names: str) -> str:
        """Get the schema for tables in a comma-separated list."""
        tables = table_names.split(", ")
        SQL_STATEMENT = """
SELECT
 TO_JSON_STRING(
    ARRAY_AGG(STRUCT(
      IF(is_nullable = 'YES', 'NULLABLE', 'REQUIRED') AS mode,
      column_name AS column_name,
      data_type AS data_type)
    ORDER BY ordinal_position), TRUE) AS schema
FROM
  `{}.INFORMATION_SCHEMA.COLUMNS`
WHERE
  table_name = '{}'
        """
        result_set = []
        for table in tables:
            table_name = (
                table if not "." in table else table.split(".")[-1]  # noqa: E713
            )
            table_name = table_name.replace("'", "").replace("`", "")
            job = self.db.query(SQL_STATEMENT.format(self.dataset, table_name))
            results = job.result(20)
            result_set.append({table_name: result for result in results})
        return f"{result_set}"

    async def _arun(self, table_name: str) -> str:
        raise NotImplementedError("SchemaSqlDbTool does not support async")


class ListBigQueryTool(BaseBigQueryTool, BaseTool):
    """Tool for getting tables names."""

    name = "list_tables_bigquery"
    description = """
    Useful Tool to list available tables names.
    Input is an empty string, output is a comma separated list of tables in the database."""

    def _run(self, tool_input: str = "") -> str:
        """Get the schema for a specific table."""
        tables = self.db.list_tables(self.dataset)
        return ", ".join(
            ["{}.{}".format(self.dataset, table.table_id) for table in tables]
        )

    async def _arun(self, tool_input: str = "") -> str:
        raise NotImplementedError("ListTablesSqlDbTool does not support async")
