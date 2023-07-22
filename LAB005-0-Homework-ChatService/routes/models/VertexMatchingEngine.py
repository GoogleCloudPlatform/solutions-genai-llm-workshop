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
# @title Vertex Matching Engine implementation
# https://github.com/GoogleCloudPlatform/generative-ai/pull/70
# Credit: https://github.com/RajeshThallam

# Do not lint this file because this is referenced from the https://github.com/GoogleCloudPlatform/generative-ai/pull/70
# flake8: noqa
from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime
from typing import Any, Iterable, List, Optional, Type

import google.auth
import google.auth.transport.requests
from google.cloud import aiplatform_v1
from google.cloud import aiplatform_v1 as aipv1
from google.cloud import storage
from google.cloud.aiplatform import MatchingEngineIndex, MatchingEngineIndexEndpoint
from google.oauth2.service_account import Credentials
from google.protobuf import struct_pb2
from langchain.docstore.document import Document
from langchain.embeddings import TensorflowHubEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.vectorstores.base import VectorStore

logger = logging.getLogger()


class MatchingEngine(VectorStore):
    """Vertex Matching Engine implementation of the vector store.

    While the embeddings are stored in the Matching Engine, the embedded
    documents will be stored in GCS.

    An existing Index and corresponding Endpoint are preconditions for
    using this module.

    See usage in docs/modules/indexes/vectorstores/examples/matchingengine.ipynb

    Note that this implementation is mostly meant for reading if you are
    planning to do a real time implementation. While reading is a real time
    operation, updating the index takes close to one hour."""

    def __init__(
        self,
        project_id: str,
        region: str,
        index: MatchingEngineIndex,
        endpoint: MatchingEngineIndexEndpoint,
        embedding: Embeddings,
        gcs_client: storage.Client,
        index_client: aiplatform_v1.IndexServiceClient,
        index_endpoint_client: aiplatform_v1.IndexEndpointServiceClient,
        gcs_bucket_name: str,
        credentials: Credentials = None,
    ):
        """Vertex Matching Engine implementation of the vector store.

        While the embeddings are stored in the Matching Engine, the embedded
        documents will be stored in GCS.

        An existing Index and corresponding Endpoint are preconditions for
        using this module.

        See usage in
        docs/modules/indexes/vectorstores/examples/matchingengine.ipynb.

        Note that this implementation is mostly meant for reading if you are
        planning to do a real time implementation. While reading is a real time
        operation, updating the index takes close to one hour.

        Attributes:
            project_id: The GCS project id.
            index: The created index class. See
            ~:func:`MatchingEngine.from_components`.
            endpoint: The created endpoint class. See
            ~:func:`MatchingEngine.from_components`.
            embedding: A :class:`Embeddings` that will be used for
            embedding the text sent. If none is sent, then the
            multilingual Tensorflow Universal Sentence Encoder will be used.
            gcs_client: The Google Cloud Storage client.
            credentials (Optional): Created GCP credentials.
        """
        super().__init__()
        self._validate_google_libraries_installation()

        self.project_id = project_id
        self.region = region
        self.index = index
        self.endpoint = endpoint
        self.embedding = embedding
        self.gcs_client = gcs_client
        self.index_client = index_client
        self.index_endpoint_client = index_endpoint_client
        self.gcs_client = gcs_client
        self.credentials = credentials
        self.gcs_bucket_name = gcs_bucket_name

    def _validate_google_libraries_installation(self) -> None:
        """Validates that Google libraries that are needed are installed."""
        try:
            from google.cloud import aiplatform, storage  # noqa: F401
            from google.oauth2 import service_account  # noqa: F401
        except ImportError:
            raise ImportError(
                "You must run `pip install --upgrade "
                "google-cloud-aiplatform google-cloud-storage`"
                "to use the MatchingEngine Vectorstore."
            )

    def add_texts(
        self,
        texts: Iterable[str],
        metadatas: Optional[List[dict]] = None,
        **kwargs: Any,
    ) -> List[str]:
        """Run more texts through the embeddings and add to the vectorstore.

        Args:
            texts: Iterable of strings to add to the vectorstore.
            metadatas: Optional list of metadatas associated with the texts.
            kwargs: vectorstore specific parameters.

        Returns:
            List of ids from adding the texts into the vectorstore.
        """
        logger.debug("Embedding documents.")
        print(f"***self.embedding={self.embedding}")
        embeddings = self.embedding.embed_documents(list(texts))
        insert_datapoints_payload = []
        ids = []

        # Streaming index update
        for idx, (embedding, text) in enumerate(zip(embeddings, texts)):
            id = uuid.uuid4()
            self._upload_to_gcs(text, f"documents/{id}")
            insert_datapoints_payload.append(
                aiplatform_v1.IndexDatapoint(
                    datapoint_id=str(id), feature_vector=embedding
                )
            )
            if idx % 100 == 0:
                upsert_request = aiplatform_v1.UpsertDatapointsRequest(
                    index=self.index.name, datapoints=insert_datapoints_payload
                )
                response = self.index_client.upsert_datapoints(request=upsert_request)
                insert_datapoints_payload = []

        upsert_request = aiplatform_v1.UpsertDatapointsRequest(
            index=self.index.name, datapoints=insert_datapoints_payload
        )
        response = self.index_client.upsert_datapoints(request=upsert_request)

        logger.debug("Updated index with new configuration.")

        return ids

    def _upload_to_gcs(self, data: str, gcs_location: str) -> None:
        """Uploads data to gcs_location.

        Args:
            data: The data that will be stored.
            gcs_location: The location where the data will be stored.
        """
        bucket = self.gcs_client.get_bucket(self.gcs_bucket_name)
        blob = bucket.blob(gcs_location)
        blob.upload_from_string(data)

    def get_matches(
        self,
        embeddings: List[str],
        n_matches: int,
        index_endpoint: MatchingEngineIndexEndpoint,
    ) -> str:
        """
        get matches from matching engine given a vector query
        Uses public endpoint
        """
        import json
        from typing import List

        import requests

        request_data = {
            "deployed_index_id": index_endpoint.deployed_indexes[0].id,
            "queries": [
                {
                    "datapoint": {"datapoint_id": f"{i}", "feature_vector": emb},
                    "neighbor_count": n_matches,
                }
                for i, emb in enumerate(embeddings)
            ],
        }

        endpoint_address = self.endpoint.public_endpoint_domain_name
        rpc_address = f"https://{endpoint_address}/v1beta1/{index_endpoint.resource_name}:findNeighbors"
        endpoint_json_data = json.dumps(request_data)

        logger.debug(f"Querying Matching Engine Index Endpoint {rpc_address}")

        header = {"Authorization": "Bearer " + self.credentials.token}

        return requests.post(rpc_address, data=endpoint_json_data, headers=header)

    def similarity_search(
        self, query: str, k: int = 4, **kwargs: Any
    ) -> List[Document]:
        """Return docs most similar to query.

        Args:
            query: The string that will be used to search for similar documents.
            k: The amount of neighbors that will be retrieved.

        Returns:
            A list of k matching documents.
        """

        logger.debug(f"Embedding query {query}.")
        embedding_query = self.embedding.embed_documents([query])
        deployed_index_id = self._get_index_id()
        logger.debug(f"Deployed Index ID = {deployed_index_id}")

        # TO-DO: Pending query sdk integration
        # response = self.endpoint.match(
        #     deployed_index_id=self._get_index_id(),
        #     queries=embedding_query,
        #     num_neighbors=k,
        # )

        response = self.get_matches(embedding_query, k, self.endpoint)

        if response.status_code == 200:
            response = response.json()["nearestNeighbors"]
        else:
            raise Exception(f"Failed to query index {str(response)}")

        if len(response) == 0:
            return []

        logger.debug(f"Found {len(response)} matches for the query {query}.")

        results = []

        # I'm only getting the first one because queries receives an array
        # and the similarity_search method only recevies one query. This
        # means that the match method will always return an array with only
        # one element.
        for doc in response[0]["neighbors"]:
            page_content = self._download_from_gcs(
                f"documents/{doc['datapoint']['datapointId']}"
            )
            results.append(Document(page_content=page_content))

        logger.debug("Downloaded documents for query.")

        return results

    def _get_index_id(self) -> str:
        """Gets the correct index id for the endpoint.

        Returns:
            The index id if found (which should be found) or throws
            ValueError otherwise.
        """
        for index in self.endpoint.deployed_indexes:
            if index.index == self.index.name:
                return index.id

        raise ValueError(
            f"No index with id {self.index.name} "
            f"deployed on enpoint "
            f"{self.endpoint.display_name}."
        )

    def _download_from_gcs(self, gcs_location: str) -> str:
        """Downloads from GCS in text format.

        Args:
            gcs_location: The location where the file is located.

        Returns:
            The string contents of the file.
        """
        bucket = self.gcs_client.get_bucket(self.gcs_bucket_name)
        try:
            blob = bucket.blob(gcs_location)
            return blob.download_as_string()
        except Exception as e:
            return ""

    @classmethod
    def from_texts(
        cls: Type["MatchingEngine"],
        texts: List[str],
        embedding: Embeddings,
        metadatas: Optional[List[dict]] = None,
        **kwargs: Any,
    ) -> "MatchingEngine":
        """Use from components instead."""
        raise NotImplementedError(
            "This method is not implemented. Instead, you should initialize the class"
            " with `MatchingEngine.from_components(...)` and then call "
            "`from_texts`"
        )

    @classmethod
    def from_documents(
        cls: Type["MatchingEngine"],
        documents: List[str],
        embedding: Embeddings,
        metadatas: Optional[List[dict]] = None,
        **kwargs: Any,
    ) -> "MatchingEngine":
        """Use from components instead."""
        raise NotImplementedError(
            "This method is not implemented. Instead, you should initialize the class"
            " with `MatchingEngine.from_components(...)` and then call "
            "`from_documents`"
        )

    @classmethod
    def from_components(
        cls: Type["MatchingEngine"],
        project_id: str,
        region: str,
        gcs_bucket_name: str,
        index_id: str,
        endpoint_id: str,
        credentials_path: Optional[str] = None,
        embedding: Optional[Embeddings] = None,
    ) -> "MatchingEngine":
        """Takes the object creation out of the constructor.

        Args:
            project_id: The GCP project id.
            region: The default location making the API calls. It must have
            the same location as the GCS bucket and must be regional.
            gcs_bucket_name: The location where the vectors will be stored in
            order for the index to be created.
            index_id: The id of the created index.
            endpoint_id: The id of the created endpoint.
            credentials_path: (Optional) The path of the Google credentials on
            the local file system.
            embedding: The :class:`Embeddings` that will be used for
            embedding the texts.

        Returns:
            A configured MatchingEngine with the texts added to the index.
        """
        gcs_bucket_name = cls._validate_gcs_bucket(gcs_bucket_name)

        # Set credentials
        if credentials_path:
            credentials = cls._create_credentials_from_file(credentials_path)
        else:
            credentials, _ = google.auth.default()
            request = google.auth.transport.requests.Request()
            credentials.refresh(request)

        index = cls._create_index_by_id(index_id, project_id, region, credentials)
        endpoint = cls._create_endpoint_by_id(
            endpoint_id, project_id, region, credentials
        )

        gcs_client = cls._get_gcs_client(credentials, project_id)
        index_client = cls._get_index_client(project_id, region, credentials)
        index_endpoint_client = cls._get_index_endpoint_client(
            project_id, region, credentials
        )
        cls._init_aiplatform(project_id, region, gcs_bucket_name, credentials)

        return cls(
            project_id=project_id,
            region=region,
            index=index,
            endpoint=endpoint,
            embedding=embedding or cls._get_default_embeddings(),
            gcs_client=gcs_client,
            index_client=index_client,
            index_endpoint_client=index_endpoint_client,
            credentials=credentials,
            gcs_bucket_name=gcs_bucket_name,
        )

    @classmethod
    def _validate_gcs_bucket(cls, gcs_bucket_name: str) -> str:
        """Validates the gcs_bucket_name as a bucket name.

        Args:
              gcs_bucket_name: The received bucket uri.

        Returns:
              A valid gcs_bucket_name or throws ValueError if full path is
              provided.
        """
        gcs_bucket_name = gcs_bucket_name.replace("gs://", "")
        if "/" in gcs_bucket_name:
            raise ValueError(
                f"The argument gcs_bucket_name should only be "
                f"the bucket name. Received {gcs_bucket_name}"
            )
        return gcs_bucket_name

    @classmethod
    def _create_credentials_from_file(
        cls, json_credentials_path: Optional[str]
    ) -> Optional[Credentials]:
        """Creates credentials for GCP.

        Args:
             json_credentials_path: The path on the file system where the
             credentials are stored.

         Returns:
             An optional of Credentials or None, in which case the default
             will be used.
        """

        from google.oauth2 import service_account

        credentials = None
        if json_credentials_path is not None:
            credentials = service_account.Credentials.from_service_account_file(
                json_credentials_path
            )

        return credentials

    @classmethod
    def _create_index_by_id(
        cls, index_id: str, project_id: str, region: str, credentials: "Credentials"
    ) -> MatchingEngineIndex:
        """Creates a MatchingEngineIndex object by id.

        Args:
            index_id: The created index id.

        Returns:
            A configured MatchingEngineIndex.
        """

        logger.debug(f"Creating matching engine index with id {index_id}.")
        index_client = cls._get_index_client(project_id, region, credentials)
        request = aiplatform_v1.GetIndexRequest(name=index_id)
        return index_client.get_index(request=request)

    @classmethod
    def _create_endpoint_by_id(
        cls, endpoint_id: str, project_id: str, region: str, credentials: "Credentials"
    ) -> MatchingEngineIndexEndpoint:
        """Creates a MatchingEngineIndexEndpoint object by id.

        Args:
            endpoint_id: The created endpoint id.

        Returns:
            A configured MatchingEngineIndexEndpoint.
            :param project_id:
            :param region:
            :param credentials:
        """

        from google.cloud import aiplatform

        logger.debug(f"Creating endpoint with id {endpoint_id}.")
        return aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=endpoint_id,
            project=project_id,
            location=region,
            credentials=credentials,
        )

    @classmethod
    def _get_gcs_client(
        cls, credentials: "Credentials", project_id: str
    ) -> "storage.Client":
        """Lazily creates a GCS client.

        Returns:
            A configured GCS client.
        """

        from google.cloud import storage

        return storage.Client(credentials=credentials, project=project_id)

    @classmethod
    def _get_index_client(
        cls, project_id: str, region: str, credentials: "Credentials"
    ) -> "storage.Client":
        """Lazily creates a Matching Engine Index client.

        Returns:
            A configured Matching Engine Index client.
        """

        PARENT = f"projects/{project_id}/locations/{region}"
        ENDPOINT = f"{region}-aiplatform.googleapis.com"
        return aiplatform_v1.IndexServiceClient(
            client_options=dict(api_endpoint=ENDPOINT), credentials=credentials
        )

    @classmethod
    def _get_index_endpoint_client(
        cls, project_id: str, region: str, credentials: "Credentials"
    ) -> "storage.Client":
        """Lazily creates a Matching Engine Index Endpoint client.

        Returns:
            A configured Matching Engine Index Endpoint client.
        """

        PARENT = f"projects/{project_id}/locations/{region}"
        ENDPOINT = f"{region}-aiplatform.googleapis.com"
        return aiplatform_v1.IndexEndpointServiceClient(
            client_options=dict(api_endpoint=ENDPOINT), credentials=credentials
        )

    @classmethod
    def _init_aiplatform(
        cls,
        project_id: str,
        region: str,
        gcs_bucket_name: str,
        credentials: "Credentials",
    ) -> None:
        """Configures the aiplatform library.

        Args:
            project_id: The GCP project id.
            region: The default location making the API calls. It must have
            the same location as the GCS bucket and must be regional.
            gcs_bucket_name: GCS staging location.
            credentials: The GCS Credentials object.
        """

        from google.cloud import aiplatform

        logger.debug(
            f"Initializing AI Platform for project {project_id} on "
            f"{region} and for {gcs_bucket_name}."
        )
        aiplatform.init(
            project=project_id,
            location=region,
            staging_bucket=gcs_bucket_name,
            credentials=credentials,
        )

    @classmethod
    def _get_default_embeddings(cls) -> TensorflowHubEmbeddings:
        """This function returns the default embedding."""
        return TensorflowHubEmbeddings()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


class MatchingEngineUtils:
    def __init__(self, project_id: str, region: str, index_name: str):
        self.project_id = project_id
        self.region = region
        self.index_name = index_name
        self.index_endpoint_name = f"{self.index_name}-endpoint"
        self.PARENT = f"projects/{self.project_id}/locations/{self.region}"

        ENDPOINT = f"{self.region}-aiplatform.googleapis.com"
        # set index client
        self.index_client = aipv1.IndexServiceClient(
            client_options=dict(api_endpoint=ENDPOINT)
        )
        # set index endpoint client
        self.index_endpoint_client = aipv1.IndexEndpointServiceClient(
            client_options=dict(api_endpoint=ENDPOINT)
        )

    def get_index(self):
        # Check if index exists
        request = aipv1.ListIndexesRequest(parent=self.PARENT)
        page_result = self.index_client.list_indexes(request=request)
        indexes = [
            response.name
            for response in page_result
            if response.display_name == self.index_name
        ]

        if len(indexes) == 0:
            return None
        else:
            index_id = indexes[0]
            request = aipv1.GetIndexRequest(name=index_id)
            index = self.index_client.get_index(request=request)
            return index

    def get_index_endpoint(self):
        # Check if index endpoint exists
        request = aipv1.ListIndexEndpointsRequest(parent=self.PARENT)
        page_result = self.index_endpoint_client.list_index_endpoints(request=request)
        index_endpoints = [
            response.name
            for response in page_result
            if response.display_name == self.index_endpoint_name
        ]

        if len(index_endpoints) == 0:
            return None
        else:
            index_endpoint_id = index_endpoints[0]
            request = aipv1.GetIndexEndpointRequest(name=index_endpoint_id)
            index_endpoint = self.index_endpoint_client.get_index_endpoint(
                request=request
            )
            return index_endpoint

    def create_index(self, embedding_gcs_uri: str, dimensions: int):
        # Get index
        index = self.get_index()
        # Create index if does not exists
        if index:
            logger.info(f"Index {self.index_name} already exists with id {index.name}")
        else:
            logger.info(f"Index {self.index_name} does not exists. Creating index ...")

            treeAhConfig = struct_pb2.Struct(
                fields={
                    "leafNodeEmbeddingCount": struct_pb2.Value(number_value=500),
                    "leafNodesToSearchPercent": struct_pb2.Value(number_value=7),
                }
            )
            algorithmConfig = struct_pb2.Struct(
                fields={"treeAhConfig": struct_pb2.Value(struct_value=treeAhConfig)}
            )
            config = struct_pb2.Struct(
                fields={
                    "dimensions": struct_pb2.Value(number_value=dimensions),
                    "approximateNeighborsCount": struct_pb2.Value(number_value=150),
                    "distanceMeasureType": struct_pb2.Value(
                        string_value="DOT_PRODUCT_DISTANCE"
                    ),
                    "algorithmConfig": struct_pb2.Value(struct_value=algorithmConfig),
                    "shardSize": struct_pb2.Value(string_value="SHARD_SIZE_SMALL"),
                }
            )
            metadata = struct_pb2.Struct(
                fields={
                    "config": struct_pb2.Value(struct_value=config),
                    "contentsDeltaUri": struct_pb2.Value(
                        string_value=embedding_gcs_uri
                    ),
                }
            )

            index_request = {
                "display_name": self.index_name,
                "description": "Index for LangChain demo",
                "metadata": struct_pb2.Value(struct_value=metadata),
                "index_update_method": aipv1.Index.IndexUpdateMethod.STREAM_UPDATE,
            }

            r = self.index_client.create_index(parent=self.PARENT, index=index_request)

            # Poll the operation until it's done successfullly.
            logging.info("Poll the operation to create index ...")
            while True:
                if r.done():
                    break
                time.sleep(60)
                print(".", end="")

            index = r.result()
            logger.info(
                f"Index {self.index_name} created with resource name as {index.name}"
            )

        return index

    def deploy_index(
        self,
        machine_type: str = "e2-standard-2",
        min_replica_count: int = 2,
        max_replica_count: int = 10,
        network: str = None,
    ):
        try:
            # Get index if exists
            index = self.get_index()
            if not index:
                raise Exception(
                    f"Index {self.index_name} does not exists. Please create index before deploying."
                )

            # Get index endpoint if exists
            index_endpoint = self.get_index_endpoint()
            # Create Index Endpoint if does not exists
            if index_endpoint:
                logger.info(
                    f"Index endpoint {self.index_endpoint_name} already exists with resource "
                    + f"name as {index_endpoint.name} and endpoint domain name as "
                    + f"{index_endpoint.public_endpoint_domain_name}"
                )
            else:
                logger.info(
                    f"Index endpoint {self.index_endpoint_name} does not exists. Creating index endpoint..."
                )
                index_endpoint_request = {"display_name": self.index_endpoint_name}

                if network:
                    index_endpoint_request["network"] = network
                else:
                    index_endpoint_request["public_endpoint_enabled"] = True

                r = self.index_endpoint_client.create_index_endpoint(
                    parent=self.PARENT, index_endpoint=index_endpoint_request
                )

                logger.info("Poll the operation to create index endpoint ...")
                while True:
                    if r.done():
                        break
                    time.sleep(60)
                    print(".", end="")

                index_endpoint = r.result()
                logger.info(
                    f"Index endpoint {self.index_endpoint_name} created with resource "
                    + f"name as {index_endpoint.name} and endpoint domain name as "
                    + f"{index_endpoint.public_endpoint_domain_name}"
                )
        except Exception as e:
            logger.error(f"Failed to create index endpoint {self.index_endpoint_name}")
            raise e

        # Deploy Index to endpoint
        try:
            # Check if index is already deployed to the endpoint
            for d_index in index_endpoint.deployed_indexes:
                if d_index.index == index.name:
                    logger.info(
                        f"Skipping deploying Index. Index {self.index_name}"
                        + f"already deployed with id {index.name} to the index endpoint {self.index_endpoint_name}"
                    )
                    return index_endpoint

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            deployed_index_id = f"{self.index_name.replace('-', '_')}_{timestamp}"
            deploy_index = {
                "id": deployed_index_id,
                "display_name": deployed_index_id,
                "index": index.name,
                "dedicated_resources": {
                    "machine_spec": {
                        "machine_type": machine_type,
                    },
                    "min_replica_count": min_replica_count,
                    "max_replica_count": max_replica_count,
                },
            }
            logger.info(f"Deploying index with request = {deploy_index}")
            r = self.index_endpoint_client.deploy_index(
                index_endpoint=index_endpoint.name, deployed_index=deploy_index
            )

            # Poll the operation until it's done successfullly.
            logger.info("Poll the operation to deploy index ...")
            while True:
                if r.done():
                    break
                time.sleep(60)
                print(".", end="")
            logger.info(
                f"Deployed index {self.index_name} to endpoint {self.index_endpoint_name}"
            )

        except Exception as e:
            logger.error(
                f"Failed to deploy index {self.index_name} to the index endpoint {self.index_endpoint_name}"
            )
            raise e

        return index_endpoint

    def get_index_and_endpoint(self):
        # Get index id if exists
        index = self.get_index()
        index_id = index.name if index else ""

        # Get index endpoint id if exists
        index_endpoint = self.get_index_endpoint()
        index_endpoint_id = index_endpoint.name if index_endpoint else ""

        return index_id, index_endpoint_id

    def delete_index(self):
        # Check if index exists
        index = self.get_index()

        # create index if does not exists
        if index:
            # Delete index
            index_id = index.name
            logger.info(f"Deleting Index {self.index_name} with id {index_id}")
            self.index_client.delete_index(name=index_id)
        else:
            raise Exception("Index {index_name} does not exists.")

    def delete_index_endpoint(self):
        # Check if index endpoint exists
        index_endpoint = self.get_index_endpoint()

        # Create Index Endpoint if does not exists
        if index_endpoint:
            logger.info(
                f"Index endpoint {self.index_endpoint_name}  exists with resource "
                + f"name as {index_endpoint.name} and endpoint domain name as "
                + f"{index_endpoint.public_endpoint_domain_name}"
            )

            index_endpoint_id = index_endpoint.name
            index_endpoint = self.index_endpoint_client.get_index_endpoint(
                name=index_endpoint_id
            )
            # Undeploy existing indexes
            for d_index in index_endpoint.deployed_indexes:
                logger.info(
                    f"Undeploying index with id {d_index.id} from Index endpoint {self.index_endpoint_name}"
                )
                request = aipv1.UndeployIndexRequest(
                    index_endpoint=index_endpoint_id, deployed_index_id=d_index.id
                )
                r = self.index_endpoint_client.undeploy_index(request=request)
                response = r.result()
                logger.info(response)

            # Delete index endpoint
            logger.info(
                f"Deleting Index endpoint {self.index_endpoint_name} with id {index_endpoint_id}"
            )
            self.index_endpoint_client.delete_index_endpoint(name=index_endpoint_id)
        else:
            raise Exception(
                f"Index endpoint {self.index_endpoint_name} does not exists."
            )
