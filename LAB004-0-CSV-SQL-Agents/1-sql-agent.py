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

from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain_experimental.sql import SQLDatabaseChain
from langchain.llms.vertexai import VertexAI
from langchain.sql_database import SQLDatabase
from sqlalchemy import *  # noqa: F403,F401
from sqlalchemy.engine import create_engine
from sqlalchemy.schema import *  # noqa: F403, F401
from sqlalchemy.sql.schema import MetaData

"""
Create Vertex LLM
"""

vertex_llm = VertexAI(
    max_output_tokens=1024,
    temperature=0,
    top_p=1,
    top_k=40,
    verbose=True,
)

"""
SQL Agent
"""

project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_REGIN")
dataset_id = "chicago_crimes"
table_name = "crimes"


table_uri = f"bigquery://{project_id}/{dataset_id}"
db = SQLDatabase.from_uri(table_uri)
toolkit = SQLDatabaseToolkit(db=db, llm=vertex_llm)

def ask_bq(question):
    agent_executor = create_sql_agent(
        llm=vertex_llm,
        toolkit=toolkit,
        verbose=True, 
        max_execution_time=60,
    )

    output = agent_executor.run(question)
    return output

output = ask_bq("what's the top 10 block, type by crime activities")

print(
    f"""
result:{output}
"""
)
