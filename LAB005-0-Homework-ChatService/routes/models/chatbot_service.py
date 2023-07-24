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

from langchain.agents import ConversationalChatAgent
from langchain.llms.vertexai import VertexAI
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from PDF_Search import VIAI_INFO_ME  # noqa: E402
from VertexLLMAgent import VertexLLMChatOutputParser  # noqa: E402

"""
Vertex AI Initialize
"""
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
REGION = os.getenv("GOOGLE_CLOUD_REGIN")

llm = VertexAI(max_output_tokens=1024)

viai_info = VIAI_INFO_ME()
tools = [
    Tool(name=viai_info.name, func=viai_info.run, description=(viai_info.description))
]


def predict(query: str) -> str:
    print("predict:creating ConversationalChatAgent...")
    a = ConversationalChatAgent.from_llm_and_tools(
        llm=llm,
        tools=tools,
        memory=memory,
        verbose=True,
        output_parser=VertexLLMChatOutputParser(),
    )
    from langchain.agents import AgentExecutor

    print("predict:loading agent executor...")
    agent = AgentExecutor.from_agent_and_tools(agent=a, tools=tools, memory=memory)
    print("predict:running agent executor...")
    result = agent.run({"input": query})
    return result


if __name__ == "__main__":
    query = "hello, I am Michael Chi, what's your name ?"
    result = predict(query=query)
    print(
        f"""
    Q:{query}
    A:{result}
    """
    )

    query = "who created the game The legend of Helda?"
    result = predict(query=query)
    print(
        f"""
    Q:{query}
    A:{result}
    """
    )

    query = "say my name please?"
    result = predict(query=query)
    print(
        f"""
    Q:{query}
    A:{result}
    """
    )

    query = "I am looking for materials that are fireproof, can you suggest me two or three of them ??"
    result = predict(query=query)
    print(
        f"""
    Q:{query}
    A:{result}
    """
    )

    query = "among these materials, which are waterproof as well ?"
    result = predict(query=query)
    print(
        f"""
    Q:{query}
    A:{result}
    """
    )

    query = "say my name again please ?"
    result = predict(query=query)
    print(
        f"""
    Q:{query}
    A:{result}
    """
    )
