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
from typing import Any, List, Tuple, Union

from langchain import SerpAPIWrapper
from langchain.agents import AgentExecutor, BaseSingleActionAgent, Tool
from langchain.llms.vertexai import VertexAI
from langchain.schema import AgentAction, AgentFinish

script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(script_dir, "../modules"))

from langchain.embeddings.vertexai import VertexAIEmbeddings  # noqa: E402

"""
Create Vertex LLM
"""

REQUESTS_PER_MINUTE = 30

llm = VertexAI(
    max_output_tokens=1024,
    temperature=0,
    top_p=0.8,
    top_k=40,
    verbose=True,
)
embeddings = VertexAIEmbeddings()

"""
Tools
"""
search = SerpAPIWrapper()
tools = [
    Tool(
        name="Search",
        func=search.run,
        description="useful for when you need to answer questions about current events",
        return_direct=True,
    )
]

"""
Agent Class
"""


class MyCustomAgent(BaseSingleActionAgent):
    """My Custom Agent."""

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
        return AgentAction(tool="Search", tool_input=kwargs["input"], log="")

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
        return AgentAction(tool="Search", tool_input=kwargs["input"], log="")


"""
Run
"""
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=MyCustomAgent(), tools=tools, verbose=True
)
result = agent_executor.run("How many people live in taiwan as of 2023?")

print(result)
