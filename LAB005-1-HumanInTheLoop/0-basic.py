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
from langchain.tools import HumanInputRun
from langchain.utilities import SerpAPIWrapper

llm = VertexAI(temperature=0.2)

def get_input() -> str:
    text = input('Input your text. Press Enter to end.\n')
    return text


search = SerpAPIWrapper()
tools = [
    HumanInputRun(
        input_func=get_input,
        description=(
            "Use this tool to ask a human to input a question"
            "The input should be a question for the human."
        ),
    ),
    Tool(
        name="Search",
        func=search.run,
        description=("useful for when you need to answer questions"),
    ),
]

agent_chain = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

result = agent_chain.run("I have a question")
print(result)
