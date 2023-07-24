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
from typing import List

from langchain.chains import RetrievalQA
from langchain.chains.conversational_retrieval.base import (
    BaseConversationalRetrievalChain,
)
from langchain.llms.vertexai import VertexAI
from langchain.memory import ConversationBufferMemory
from langchain.tools import BaseTool

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from MyVertexAIEmbedding import MyVertexAIEmbedding  # noqa: E402
from VertexMatchingEngine import MatchingEngine, MatchingEngineUtils  # noqa: E402

# https://cdn.cloudflare.steamstatic.com/steam/apps/597180/manuals/Old_World-Official_User_Manual.pdf?t=1653279974
"""
Matching Engine As Retriever
"""

ME_REGION = os.getenv("GOOGLE_CLOUD_REGIN")
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
ME_INDEX_NAME = f"{PROJECT_ID}-chatbot-vme"
ME_DIMENSIONS = 768
ME_EMBEDDING_DIR = f"gs://{PROJECT_ID}-chatbot-embeddings"
REQUESTS_PER_MINUTE = 15

mengine = MatchingEngineUtils(
    project_id=PROJECT_ID, region=ME_REGION, index_name=ME_INDEX_NAME
)
embedding = MyVertexAIEmbedding()

llm = VertexAI()
memory = ConversationBufferMemory()


def create_PDFQA_chain_me_RetrievalQA() -> BaseConversationalRetrievalChain:
    mengine = MatchingEngineUtils(
        project_id=PROJECT_ID, region=ME_REGION, index_name=ME_INDEX_NAME
    )
    ME_INDEX_ID, ME_INDEX_ENDPOINT_ID = mengine.get_index_and_endpoint()

    me = MatchingEngine.from_components(
        project_id=PROJECT_ID,
        region=ME_REGION,
        gcs_bucket_name=f'gs://{ME_EMBEDDING_DIR.split("/")[2]}',
        embedding=embedding,
        index_id=ME_INDEX_ID,
        endpoint_id=ME_INDEX_ENDPOINT_ID,
    )

    retriever = me.as_retriever()
    doc_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=False,
        verbose=True,
    )

    return doc_chain


class VIAI_INFO_ME(BaseTool):
    name = "VIAI_INFO_ME"
    description = """
    Use this tool to get information regarding the solution "Visual Inspection AI Edge", or "VIAI Edge".
    The Tool Input is the user's question, the user may reference to previous convsation,
    add context to the question when needed.
    The Output is the result
    """

    def _run(self, query: str) -> str:
        if query == "":
            query = "summarize"
        chat_history: List[str] = []
        print("Running tool:{}".format(query))

        qa = create_PDFQA_chain_me_RetrievalQA()
        result = qa(
            {"query": query, "chat_history": chat_history}, return_only_outputs=False
        )
        return result

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        print(f"*** Invoking MockTool with query '{query}'")
        return f"Answer of '{query}' is 'Michael Chi'"
