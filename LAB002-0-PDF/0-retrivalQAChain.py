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

from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader
from langchain.llms.vertexai import VertexAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS

script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(script_dir, "../modules"))

from langchain.embeddings.vertexai import VertexAIEmbeddings  # noqa: E402

llm = VertexAI(
    max_output_tokens=256,
    temperature=0.1,
    top_p=0.8,
    top_k=40,
    verbose=True,
)

# Load Text file

loader = TextLoader("../dataset/unstructured/state_of_union.txt")
documents = loader.load()

# Chunk the file
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
documents = text_splitter.split_documents(documents)

embeddings = VertexAIEmbeddings()
# Insert the file to FAISS and  create a VectorStore client

print("FAISS.from_documents()...")
vectorstore = FAISS.from_documents(documents, embeddings)
# Create a Retriever
# See: https://python.langchain.com/en/latest/modules/indexes/retrievers.html
print("vectorstore.as_retriever()...")
retriever = vectorstore.as_retriever()

# Create RetrievalQA Chain
# See: https://python.langchain.com/en/latest/modules/chains/index_examples/vector_db_qa.html
print("Creating Chain...")

qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)
query = "what did he say about protecting women rights"
print("Sending Question:{}".format(query))
result = qa({"query": query})
print(result["result"])
