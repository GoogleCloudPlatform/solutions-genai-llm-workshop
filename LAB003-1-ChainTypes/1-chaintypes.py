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
from google.cloud import secretmanager
from langchain.chains import RetrievalQA
from langchain.document_loaders import PyPDFLoader
from langchain.llms.vertexai import VertexAI
from langchain.prompts import PromptTemplate

script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(script_dir, "../modules"))

from langchain.embeddings.vertexai import VertexAIEmbeddings  # noqa: E402
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS


"""
Vertex AI Initialize
"""


PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
REGION = os.getenv("GOOGLE_CLOUD_REGION")

vertexai.init(project=PROJECT_ID, location=REGION)

llm = VertexAI(max_output_tokens=1024)

embedding = VertexAIEmbeddings()

"""
Create Retriever
"""
documents = PyPDFLoader(file_path="../dataset/pdf/VIAI.pdf").load_and_split()
vectors = FAISS.from_documents(documents=documents, embedding=embedding)
retriever = vectors.as_retriever()

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


query = "what does the solution do ?"
ask(query)
