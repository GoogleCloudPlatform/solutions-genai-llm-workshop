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
from langchain.indexes.vectorstore import VectorstoreIndexCreator
from langchain.llms import VertexAI
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
embeddings = VertexAIEmbeddings()

index_name = "state_of_union"

PDF_FILE = f"../dataset/unstructured/{index_name}.txt"
loader = TextLoader(PDF_FILE)
documents = loader.load()

index = VectorstoreIndexCreator(
    text_splitter=CharacterTextSplitter(chunk_size=1000, chunk_overlap=10),
    embedding=embeddings,
    vectorstore_cls=FAISS,
).from_loaders([loader])

query = "What did the president say about Justice Breyer"
result = index.query(query, llm=llm, chain_type="stuff")
print(result)
