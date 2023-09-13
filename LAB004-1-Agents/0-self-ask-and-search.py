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
from langchain import SerpAPIWrapper
from langchain.agents import AgentType, Tool, initialize_agent
from langchain.llms.vertexai import VertexAI

"""
Create Vertex LLM
"""

llm = VertexAI(max_output_tokens=1024, verbose=True, temperature=0)

"""
Load Tools
"""
search = SerpAPIWrapper()
tools = [
    Tool(
        verbose=True,
        name="Intermediate Answer",
        func=search.run,
        description="useful for when you need to ask with search",
    )
]
agent_executor = initialize_agent(
    tools, llm, agent=AgentType.SELF_ASK_WITH_SEARCH, verbose=True
)
result = agent_executor.run("how many people live in Taipei City ?")
print(result)
