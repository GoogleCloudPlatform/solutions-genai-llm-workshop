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

import vertexai
from langchain.chains import RetrievalQA
from langchain.llms.vertexai import VertexAI
from langchain.prompts import PromptTemplate

script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(script_dir, "../modules"))

from MyVertexAIEmbedding import MyVertexAIEmbedding  # noqa: E402
from VertexMatchingEngine import MatchingEngine, MatchingEngineUtils  # noqa: E402

"""
Vertex AI Initialize
"""


PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
REGION = os.getenv("GOOGLE_CLOUD_REGION")

vertexai.init(project=PROJECT_ID, location=REGION)

llm = VertexAI(max_output_tokens=1024)

embedding = MyVertexAIEmbedding()

"""
Create Retriever
"""
ME_INDEX_NAME = f"{PROJECT_ID}-vme"
ME_DIMENSIONS = 768
ME_EMBEDDING_DIR = f"gs://{PROJECT_ID}-embeddings"
REQUESTS_PER_MINUTE = 300

mengine = MatchingEngineUtils(
    project_id=PROJECT_ID, region=REGION, index_name=ME_INDEX_NAME
)
ME_INDEX_ID, ME_INDEX_ENDPOINT_ID = mengine.get_index_and_endpoint()

me = MatchingEngine.from_components(
    project_id=PROJECT_ID,
    region=REGION,
    gcs_bucket_name=f'gs://{ME_EMBEDDING_DIR.split("/")[2]}',
    embedding=embedding,
    index_id=ME_INDEX_ID,
    endpoint_id=ME_INDEX_ENDPOINT_ID,
)

retriever = me.as_retriever()

# Create Custom Prompt

prompt_template = """
Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}
Answer:"""
PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)
chain_type_kwargs = {"prompt": PROMPT}

# Create RetrievalQA Chain
# See: https://python.langchain.com/en/latest/modules/chains/index_examples/vector_db_qa.html
print("Creating Chain...")

qa_stuff = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    chain_type_kwargs=chain_type_kwargs,
)
qa_refine = RetrievalQA.from_chain_type(
    llm=llm, chain_type="refine", retriever=retriever
)
qa_map_reduce = RetrievalQA.from_chain_type(
    llm=llm, chain_type="map_reduce", retriever=retriever
)
qa_map_rerank = RetrievalQA.from_chain_type(
    llm=llm, chain_type="map_rerank", retriever=retriever
)


def ask(query: str) -> None:
    result = qa_stuff({"query": query})
    print(
        f"""** stuff:
    {result['result']}
    """
    )

    result = qa_refine({"query": query})
    print(
        f"""** refine:
    {result['result']}
    """
    )

    result = qa_map_reduce({"query": query})
    print(
        f"""** map_reduce:
    {result['result']}
    """
    )

    result = qa_map_rerank({"query": query})
    print(
        f"""** map_rerank:
    {result['result']}
    """
    )

    # Similiarity Search, then In-Context learning
    # print("#########################")
    # docs=me.similarity_search(query)
    # contents = [doc.page_content.replace("\n","") for doc in docs]
    # content = '\n\n'.join(contents)
    # prompt=f"""
    # Given below document content:
    # {content}

    # Answer the question:{query}
    # """
    # result1=llm(prompt)
    # print(f"{result1}")


query = "what deployment options are available ?"
ask(query)
