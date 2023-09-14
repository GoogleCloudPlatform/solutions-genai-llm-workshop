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
from typing import Any, List, Tuple, Union

from langchain.agents import BaseSingleActionAgent
from langchain.schema import AgentAction, AgentFinish


class CustomBQAgent(BaseSingleActionAgent):
    """
    Custom Agent that answer questions by fetching BQ data.
    * When user ask a question, the agent:
    1. check available table schema in the BQ dataset
    2. retrieve table schemas
    3. convert the question to SQL statement
    4. execute SQL query
    5. return result set to the user
    """

    @property
    def input_keys(self):
        return ["input"]

    def plan(
        self, intermediate_steps: List[Tuple[AgentAction, str]], **kwargs: Any
    ) -> Union[AgentAction, AgentFinish]:
        """Given input, decided what to do.

        Args:
            intermediate_steps: Steps the LLM has taken to date,
                along with observations
            **kwargs: User inputs.

        Returns:
            Action specifying what tool to use.
        """
        # print(f"***kwargs[input]={kwargs['input']}")
        if intermediate_steps == []:
            return AgentAction(tool="list_tables_bigquery", tool_input="", log="")

        previous_action, previous_obversation = intermediate_steps[-1]
        # print(f"*** {previous_action} |{previous_obversation}")
        if previous_action.tool == "list_tables_bigquery":
            return AgentAction(
                tool="schema_bigquery",
                tool_input=previous_obversation,
                log=previous_action.log,
            )

        # 只有這一步是真正需要LLM做事情的步驟：將問題轉換成SQL Statement
        if previous_action.tool == "schema_bigquery":
            return AgentAction(
                tool="create_sql_statement",
                tool_input={
                    "query": kwargs["input"],
                    "table_schema": previous_obversation,
                },
                log=previous_action.log,
            )

        if previous_action.tool == "create_sql_statement":
            return AgentAction(
                tool="query_bigquery",
                tool_input=previous_obversation,
                log=previous_action.log,
            )

        if previous_action.tool == "query_bigquery":
            return AgentFinish(
                return_values={"output": f"{previous_obversation}"},
                log=previous_action.log,
            )

        raise Exception(
            f"Unknown Step:previous_action={previous_action} | previous_obversation={previous_obversation}"
        )

    async def aplan(
        self, intermediate_steps: List[Tuple[AgentAction, str]], **kwargs: Any
    ) -> Union[AgentAction, AgentFinish]:
        """Given input, decided what to do.

        Args:
            intermediate_steps: Steps the LLM has taken to date,
                along with observations
            **kwargs: User inputs.

        Returns:
            Action specifying what tool to use.
        """
        raise NotImplementedError("The CustomBQAgent does not support Async calls.")
