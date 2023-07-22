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

from langchain import LLMChain, SerpAPIWrapper
from langchain.agents import AgentExecutor, LLMSingleActionAgent, Tool
from langchain.llms.vertexai import VertexAI

script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(script_dir, "../modules"))

from MyVertexAIEmbedding import MyVertexAIEmbedding  # noqa: E402
from VertexLLMPrompt import VertexPromptTemplate  # noqa: E402
from VertexLLMPrompt import VertexLLMOutputParser  # noqa: E402; noqa: E402

"""
Create Vertex LLM
"""

llm = VertexAI(
    max_output_tokens=1024,
    temperature=0,
    top_p=0.8,
    top_k=40,
    verbose=True,
)
embeddings = MyVertexAIEmbedding()

"""
Load Tools
"""

search = SerpAPIWrapper()
tools = [
    Tool(
        name="Search",
        func=search.run,
        description="useful for when you need to answer questions about current events",
    ),
]

prompt = VertexPromptTemplate(
    tools=tools,
    input_variables=["input", "intermediate_steps"],
)


llm_chain = LLMChain(llm=llm, prompt=prompt)

output_parser = VertexLLMOutputParser()
tool_names = [tool.name for tool in tools]
agent = LLMSingleActionAgent(
    llm_chain=llm_chain,
    output_parser=output_parser,
    stop=["\nObservation:"],
    allowed_tools=tool_names,
)
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent, tools=tools, verbose=True
)

result = agent_executor.run(input="What's Taipei City's population?")

print("*****")
print(result)
