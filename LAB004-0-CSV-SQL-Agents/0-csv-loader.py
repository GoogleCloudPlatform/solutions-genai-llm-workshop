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

from langchain.agents import create_csv_agent
from langchain.llms.vertexai import VertexAI

script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(script_dir, "../modules"))

from VertexLLMPrompt import VertexLLMOutputParser  # noqa: E402

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
Load Documents into Vector Store
"""

CSV_FILE = "../dataset/csv/chicago-crimes-50000.csv"
agent = create_csv_agent(
    vertex_llm, CSV_FILE, verbose=True, output_parser=VertexLLMOutputParser()
)

query = "how many records ?"
result = agent.run(input=query, verbose=True)
print(
    f"""
===========
Answer to your query:{query}, is
{result}
===========
"""
)

query = "count how many crime records happend after 2010-12-31 ?"
result = agent.run(input=query, verbose=True)
print(
    f"""
===========
Answer to your query:{query}, is
{result}
===========
"""
)
