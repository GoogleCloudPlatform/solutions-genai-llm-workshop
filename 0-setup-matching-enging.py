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
import json
import os
import sys
import uuid
from typing import List

import numpy as np
from google.cloud import storage
from langchain.document_loaders import PyPDFLoader
from langchain.llms.vertexai import VertexAI
from langchain.schema import BaseRetriever, Document

script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(script_dir, "modules"))

from MyVertexAIEmbedding import MyVertexAIEmbedding  # noqa: E402
from VertexMatchingEngine import MatchingEngine, MatchingEngineUtils  # noqa: E402

ME_REGION = os.getenv("GOOGLE_CLOUD_REGION")
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
ME_INDEX_NAME = f"{PROJECT_ID}-vme"
ME_DIMENSIONS = 768
ME_EMBEDDING_DIR = f"gs://{PROJECT_ID}-embeddings"
REQUESTS_PER_MINUTE = 300
embedding = MyVertexAIEmbedding(requests_per_minute=REQUESTS_PER_MINUTE)


def init_index() -> None:
    # dummy embedding
    init_embedding = {
        "id": str(uuid.uuid4()),
        "embedding": list(np.zeros(ME_DIMENSIONS)),
    }

    # dump embedding to a local file
    with open("/tmp/embeddings_0.json", "w") as f:
        json.dump(init_embedding, f)

    # write embedding to Cloud Storage
    client = storage.Client(project=PROJECT_ID)
    bucket = client.get_bucket(f"{PROJECT_ID}-embeddings")
    blob = bucket.blob("init_index/embeddings_0.json")
    blob.upload_from_filename("/tmp/embeddings_0.json")


def load_documents(file_urls: List[str]) -> List[Document]:
    documents = []
    for url in file_urls:
        loader = PyPDFLoader(url)
        documents.extend(loader.load())
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=0)
    doc_splits = text_splitter.split_documents(documents)
    print(f"# of documents = {len(doc_splits)}")
    return doc_splits


def index_documents_and_get_retriever(documents: List[Document]) -> BaseRetriever:
    mengine = MatchingEngineUtils(
        project_id=PROJECT_ID, region=ME_REGION, index_name=ME_INDEX_NAME
    )
    index = mengine.get_index()

    if index is None:
        index = mengine.create_index(f"{ME_EMBEDDING_DIR}/init_index", ME_DIMENSIONS)
    index_endpoint = mengine.get_index_endpoint()

    if index_endpoint is None:
        index_endpoint = mengine.deploy_index()

    if index_endpoint:
        print(f"Index endpoint resource name: {index_endpoint.name}")
        print(
            f"Index endpoint public domain name: {index_endpoint.public_endpoint_domain_name}"
        )
        print("Deployed indexes on the index endpoint:")
        for d in index_endpoint.deployed_indexes:
            print(f"    {d.id}")

    ME_INDEX_ID, ME_INDEX_ENDPOINT_ID = mengine.get_index_and_endpoint()
    print(f"ME_INDEX_ID={ME_INDEX_ID}")
    print(f"ME_INDEX_ENDPOINT_ID={ME_INDEX_ENDPOINT_ID}")
    me = MatchingEngine.from_components(
        project_id=PROJECT_ID,
        region=ME_REGION,
        gcs_bucket_name=f'gs://{ME_EMBEDDING_DIR.split("/")[2]}',
        embedding=embedding,
        index_id=ME_INDEX_ID,
        endpoint_id=ME_INDEX_ENDPOINT_ID,
    )

    me.add_documents(documents)
    return me


def verify_llm(query: str) -> str:
    llm = VertexAI()

    """
    Create Retriever
    """
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
    # Create RetrievalQA Chain
    # See: https://python.langchain.com/en/latest/modules/chains/index_examples/vector_db_qa.html
    print("Creating Chain...")
    from langchain.chains import RetrievalQA

    qa = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=me.as_retriever()
    )
    print("Sending Question:{}".format(query))
    result = qa({"query": query})
    return result["result"]


PDF_FILE = "./dataset/pdf/VIAI.pdf"

init_index()
documents = load_documents([PDF_FILE])
me = index_documents_and_get_retriever(documents)

result = me.similarity_search("Who created the VIAI Edge solution?", k=2)
print(result)

result = verify_llm("Who created the VIAI Edge solution?")
print(result)
