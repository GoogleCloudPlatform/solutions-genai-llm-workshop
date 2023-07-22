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

llm = VertexAI(temperature=0.2, top_p=1, top_k=40, max_output_tokens=1024)

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

# Create RetrievalQA Chain
# See: https://python.langchain.com/en/latest/modules/chains/index_examples/vector_db_qa.html
print("Creating Chain...")

qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

query = "Who created the VIAI Edge solution??"
print("Sending Question:{}".format(query))
result = qa({"query": query})
print(result["result"])
