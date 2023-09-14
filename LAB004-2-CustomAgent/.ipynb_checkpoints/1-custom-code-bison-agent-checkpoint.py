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
import os
import sys

from google.cloud import bigquery
from langchain.agents import AgentExecutor

script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(script_dir, "../modules"))

from BigQueryToolKit_CodeBison import BigQueryToolKit_CodeBison  # noqa: E402
from CustomBQAgent import CustomBQAgent  # noqa: E402
from langchain.llms import VertexAI  # noqa: E402

agent = CustomBQAgent()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
BQ_DATASET_ID = "chicago_crimes"

db = bigquery.Client(PROJECT_ID)
toolkit = BigQueryToolKit_CodeBison(
    db=db, dataset=BQ_DATASET_ID, llm=VertexAI(model_name="code-bison")
)
tools = toolkit.get_tools()

executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True)
query = "what's the top 10 block, type by crime activities"
# query = "show me top 10 blocks, crimes, arrested cases and not arrested cases by not arrested rate."
resp = executor.run(query)
print(resp)
