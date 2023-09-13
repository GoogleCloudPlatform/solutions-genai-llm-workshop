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
from typing import List, Tuple

from langchain.chains import ConversationalRetrievalChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.document_loaders import TextLoader
from langchain.llms import VertexAI
from langchain.vectorstores import FAISS

script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(script_dir, "../modules"))

from langchain.embeddings.vertexai import VertexAIEmbeddings  # noqa: E402

llm = VertexAI(
    max_output_tokens=256,
    temperature=0,
    top_p=0.8,
    top_k=40,
    verbose=True,
)
embeddings = VertexAIEmbeddings()


PDF_FILE = "../dataset/unstructured/state_of_union.txt"
loader = TextLoader(PDF_FILE)
documents = loader.load_and_split()
vectorstore = FAISS.from_documents(documents=documents, embedding=embeddings)

doc_chain = load_qa_with_sources_chain(llm, chain_type="stuff", verbose=True)
qa = ConversationalRetrievalChain.from_llm(
    llm=llm, retriever=vectorstore.as_retriever()
)

chat_history: List[Tuple[str, str]] = []
query = "who is Justice Breyer"
result = qa({"question": query, "chat_history": chat_history}, return_only_outputs=True)
print(result["answer"])
chat_history = [(query, result["answer"])]

query = "what did the president said about him ? answer in English."
result = qa({"question": query, "chat_history": chat_history}, return_only_outputs=True)
print(result["answer"])
chat_history.append((query, result["answer"]))

query = "what does he do now ? answer in English."
result = qa({"question": query, "chat_history": chat_history}, return_only_outputs=True)
print(result["answer"])
chat_history.append((query, result["answer"]))
