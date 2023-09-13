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
from langchain.document_loaders import PyPDFLoader, UnstructuredPDFLoader
from langchain.llms.vertexai import VertexAI
script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(script_dir, "../modules"))

from langchain.embeddings.vertexai import VertexAIEmbeddings  # noqa: E402
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import PGVector

def __get_db_password() -> str:
    GOOGLE_CLOUD_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT")
    DATABASE_PWD_KEY = os.environ.get("DATABASE_PWD_KEY", "pgvector-password")
    if GOOGLE_CLOUD_PROJECT == "":
        raise Exception("GOOGLE_CLOUD_PROJECT environment variables must be set")

    client = secretmanager.SecretManagerServiceClient()

    request = secretmanager.AccessSecretVersionRequest(
        name=f"projects/{GOOGLE_CLOUD_PROJECT}/secrets/{DATABASE_PWD_KEY}/versions/latest",
    )
    response = client.access_secret_version(request)

    payload = response.payload.data.decode("UTF-8")
    return payload


def __create_pgvector(collect_name: str) -> PGVector:
    DATABASE_NAME = os.environ.get("DATABASE_NAME", "postgres")
    DATABASE_IP_ADDRESS = os.environ.get("DATABASE_IP_ADDRESS", "172.23.0.2")
    DATABASE_USER = os.environ.get("DATABASE_USER", "llmuser")
    DATABASE_PASSWORD = __get_db_password()

    CONNECTION_STRING = PGVector.connection_string_from_db_params(
        driver="psycopg2",
        host=DATABASE_IP_ADDRESS,
        port=5432,
        database=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
    )
    print(f"connection string={CONNECTION_STRING}")
    vectors = PGVector.from_existing_index(
        embedding=VertexAIEmbeddings(),
        collection_name=collect_name,
        connection_string=CONNECTION_STRING,
    )

    return vectors

"""
Vertex AI Initialize
"""

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
REGION = os.getenv("GOOGLE_CLOUD_REGION")
vertexai.init(project=PROJECT_ID, location=REGION)

llm = VertexAI(temperature=0.2, top_p=1, top_k=40, max_output_tokens=1024)

embedding = VertexAIEmbeddings()

"""
Create Retriever
"""
vectors = __create_pgvector(collect_name="test")
retriever = vectors.as_retriever()
# Create RetrievalQA Chain
# See: https://python.langchain.com/en/latest/modules/chains/index_examples/vector_db_qa.html
print("Creating Chain...")

qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

query = "輕舞飛揚的plan是什麼？"
print("Sending Question:{}".format(query))
result = qa({"query": query})
print(result["result"])
