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
from langchain.agents import AgentType, Tool, initialize_agent
from langchain.llms.vertexai import VertexAI
from MockTool import MockTool

llm = VertexAI()

mock = MockTool(verbose=True)

tools = [
    Tool(
        name=mock.name,
        func=mock.run,
        description=mock.description,
    )
]

agent = initialize_agent(
    tools=tools, llm=llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

query = "who is the spearker of this session?"
result = agent.run(query)
print(result)
