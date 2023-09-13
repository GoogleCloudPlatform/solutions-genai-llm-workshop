# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from typing import List

from google.cloud import secretmanager, storage
from langchain.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
)
from langchain.embeddings.vertexai import VertexAIEmbeddings
from langchain.vectorstores.pgvector import PGVector


def __get_db_password() -> str:
    GOOGLE_CLOUD_PROJECT = os.environ.get("PROJECT_ID")
    DATABASE_PWD_KEY = os.environ.get("DATABASE_PWD_KEY", "pgvector-password")
    if GOOGLE_CLOUD_PROJECT == "":
        raise Exception("PROJECT_ID environment variables must be set")

    client = secretmanager.SecretManagerServiceClient()

    request = secretmanager.AccessSecretVersionRequest(
        name=f"projects/{GOOGLE_CLOUD_PROJECT}/secrets/{DATABASE_PWD_KEY}/versions/latest",
    )
    response = client.access_secret_version(request)

    payload = response.payload.data.decode("UTF-8")
    return payload


def __create_pgvector(collect_name: str) -> PGVector:
    DATABASE_NAME = os.environ.get("DATABASE_NAME", "postgres")
    DATABASE_IP_ADDRESS = os.environ.get("DATABASE_IP_ADDRESS", "127.0.0.1")
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


def download_from_gcs(bucket: str, file: str) -> str:
    storage_client = storage.Client()
    bucket_object = storage_client.get_bucket(bucket)
    blob = bucket_object.blob(file)
    FILE = f"./{file.split('/')[-1]}"
    blob.download_to_filename(FILE)
    return FILE


def index(bucket: str, folder: str, file_name: str) -> List[str]:
    vectors = __create_pgvector(collect_name=folder)
    content = download_from_gcs(bucket=bucket, file=f"{folder}/{file_name}")

    extension = file_name.lower().split(".")[-1]
    documents = []
    ids = []
    if extension == "md":
        documents = UnstructuredMarkdownLoader(file_path=content).load_and_split()
    if extension == "txt":
        documents = TextLoader(file_path=content, encoding="utf-8").load_and_split()
    if extension == "pdf":
        documents = PyPDFLoader(file_path=content).load_and_split()
    if extension == "html":
        documents = UnstructuredHTMLLoader(file_path=content)
    if extension == "htm":
        documents = UnstructuredHTMLLoader(file_path=content)

    if documents != []:
        ids = vectors.add_documents(documents=documents)

    print(f"indexed file [{file_name}]: {ids}")
    return ids
