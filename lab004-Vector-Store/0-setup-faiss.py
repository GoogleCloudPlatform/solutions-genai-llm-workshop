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

from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS

script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(script_dir, "../modules"))

from MyVertexAIEmbedding import MyVertexAIEmbedding  # noqa: E402


def save_local_index(index_name: str) -> None:
    loader = TextLoader(f"../dataset/unstructured/{index_name}.txt")
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=0)
    doc_splits = text_splitter.split_documents(documents)
    embeddings = MyVertexAIEmbedding()

    print("FAISS.from_documents()...")
    vectorstore = FAISS.from_documents(doc_splits, embeddings)
    print("saving local...")
    vectorstore.save_local(folder_path="./vectorstore", index_name=index_name)


save_local_index("state_of_union")
