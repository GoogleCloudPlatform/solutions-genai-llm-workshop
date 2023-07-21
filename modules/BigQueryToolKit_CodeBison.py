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
from typing import List

from BigQueryTools_CodeBison import (
    GoogleSQLTool,
    InfoBigQueryTool,
    ListBigQueryTool,
    QueryBigQueryTool,
)
from google.cloud import bigquery
from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.tools import BaseTool
from pydantic import Field


class BigQueryToolKit_CodeBison(BaseToolkit):
    """Toolkit for interacting with SQL databases."""

    db: bigquery.Client = Field(exclude=True)
    dataset: str = Field(exclude=True)

    @property
    def dialect(self) -> str:
        """Return string representation of dialect to use."""
        return "bigquery"
        # return self.db.dialect

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit."""
        return [
            ListBigQueryTool(db=self.db, dataset=self.dataset),
            InfoBigQueryTool(db=self.db, dataset=self.dataset),
            GoogleSQLTool(db=self.db, dataset=self.dataset),
            QueryBigQueryTool(db=self.db, dataset=self.dataset),
        ]
