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
import json
import os
from typing import List

from BigQueryTools import InfoBigQueryTool, ListBigQueryTool, QueryBigQueryTool
from google.cloud import bigquery
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.llms.base import BaseLLM
from langchain.llms.vertexai import VertexAI
from langchain.tools import BaseTool, HumanInputRun
from pydantic import Field

PREFIX = """
You are a GoogleSQL expert. You know GoogleSQL and you help users to find answers from BigQuery datasets.
When you find the answer from BigQuery dataset,
you ask human which format he'd like the data to be presented and format the data as specified.
You have access to the following tools to fetch any data from BigQuery:
"""

FORMAT_INSTRUCTIONS = """
* Read user's question, check if BigQuery dataset has required tables, construct GoogleSQL.
* Review the GoogleSQL you created, make sure no errors in there.
* Make sure your GoogleSQL statements are in correct GoogleSQL format,
  and can be directly executed in BigQuery without errors.
* Make sure your GoogleSQL answers the question.
* And use tool to find answers
* If the tool returns errors:
    1. Read the error message.
    2. List reasons that cause the error
    3. Correct the error
    4. execute again.
* Use tools, DO NOT make up answers.
* Think step by step.
strictly use the following format:

Question: the input question you must answer
Thought:you should always think about what to do
Action: the action to take, should be one of [{tool_names}]. This should always be the tool name you want to use.
Action Input: the input to the action, this is required, if there is no Action Input, use 'Action Input:""'.
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Action: Human
Action Input: question to human
Observation: the format specified by the human
Final Answer: returns the formatted result.

Remember:
* if there is no Action Input, use 'Action Input:""'.
* read the error message, and think how to fix the error.
* Your answer MUST include column names
"""

SUFFIX = """Begin!

Question: {input}
Thought:{agent_scratchpad}"""


class BigQueryToolkit(BaseToolkit):
    """Toolkit for interacting with SQL databases."""

    db: bigquery.Client = Field(exclude=True)
    dataset: str = Field(exclude=True)
    llm: BaseLLM = Field(default_factory=lambda: VertexAI())

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
            QueryBigQueryTool(db=self.db, dataset=self.dataset),
            HumanInputRun(
                name="Human",
                input_func=get_input,
                description=(
                    "Use this tool to ask a human to input a format, ex: csv, markdown."
                    "The input should be a question for the human."
                ),
            ),
        ]


def get_input() -> str:
    text = input('Input your text. Press Enter to end.\n')
    return text


def predict(query: str) -> str:
    llm = VertexAI(
        model_name="text-bison@001",
        max_output_tokens=1024,
        temperature=0.5,
        top_p=1,
        top_k=40,
        verbose=True,
    )

    PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
    BQ_DATASET_ID = f"{PROJECT_ID}.chicago_crimes"

    db = bigquery.Client(PROJECT_ID)
    toolkit = BigQueryToolkit(db=db, dataset=BQ_DATASET_ID, llm=llm)
    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        format_instructions=FORMAT_INSTRUCTIONS,
        prefix=PREFIX,
        suffix=SUFFIX,
        # max_execution_time=100, #The max_execution_time (sec) can be set to limit the execution time of the loader.
        # max_iterations=10, #  It now stops nicely after a certain amount of iterations!
        # early_stopping_method = "generate" # By default,
        # the early stopping uses method force which just returns that constant string.
        # Alternatively,
        # you could specify method generate which then does one FINAL pass through the LLM to generate an output.
    )

    result = agent_executor.run(input=query)

    return json.dumps({"message": result})


if __name__ == "__main__":
    query = """
    show me top 10 blocks by crimes.
    """
    # query= """
    # show me top 10 blocks by un-arrested crimes.
    # """
    # query= """
    # show me top 10 blocks, crimes, arrested cases and un-arrested cases by un-arrested rate.
    # """
    result = predict(query)

    print(
        f"""
    Answer to your question: {query}, is:
    {result}
    """
    )
