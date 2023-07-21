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
from langchain.llms.vertexai import VertexAI
from langchain.vectorstores import FAISS

script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(script_dir, "../modules"))

from MyVertexAIEmbedding import MyVertexAIEmbedding  # noqa: E402

REQUESTS_PER_MINUTE = 30
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
index_name = "state_of_union"
llm = VertexAI(
    max_output_tokens=256,
    temperature=0.1,
    top_p=0.8,
    top_k=40,
    verbose=True,
)
embeddings = MyVertexAIEmbedding()


print("local from local...")
vectorstore = FAISS.load_local(
    "./vectorstore", embeddings=embeddings, index_name=index_name
)
print("vectorstore.as_retriever()...")
retriever = vectorstore.as_retriever()

# Create RetrievalQA Chain
# See: https://python.langchain.com/en/latest/modules/chains/index_examples/vector_db_qa.html
print("Creating Chain...")

qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

query = "what did he say about protect women rights?"
print("Sending Question:{}".format(query))
result = qa({"query": query})
print(result["result"])
