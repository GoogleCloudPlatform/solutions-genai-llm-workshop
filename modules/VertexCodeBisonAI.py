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

from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from langchain.llms.vertexai import _VertexAICommon
from typing import List, Optional


class VertexCodeBisonAI(_VertexAICommon, LLM):
    """Wrapper around Google Vertex AI large language models."""

    model_name: str = "code-bison"
    tuned_model_name: Optional[str] = None
    "The name of a tuned model, if it's provided, model_name is ignored."

    def _predict(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> str:
        REGION = os.getenv("GOOGLE_CLOUD_REGION")
        PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
        API_ENDPOINT = f"{REGION}-aiplatform.googleapis.com"
        ENDPOINT = f"projects/{PROJECT_ID}/locations/{REGION}/publishers/google/models/{self.model_name}"
        # The AI Platform services require regional API endpoints.
        client_options = {"api_endpoint": API_ENDPOINT}
        # Initialize client that will be used to create and send requests.
        # This client only needs to be created once, and can be reused for multiple requests.
        client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)
        instance_dict = {"prefix": prompt}
        instance = json_format.ParseDict(instance_dict, Value())
        instances = [instance]
        parameters = json_format.ParseDict(
            {"temperature": 0.2, "maxOutputTokens": 1024}, Value()
        )
        response = client.predict(
            endpoint=ENDPOINT,  # noqa: E501
            instances=instances,
            parameters=parameters,
        )
        predictions = response.predictions
        result = predictions[0]["content"]
        result = result.strip("```sql").strip("```")
        return result

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> str:
        """Call Vertex model to get predictions based on the prompt.

        Args:
            prompt: The prompt to pass into the model.
            stop: A list of stop words (optional).
            run_manager: A Callbackmanager for LLM run, optional.

        Returns:
            The string generated by the model.
        """
        return self._predict(prompt, stop)


if __name__ == "__main__":
    vertex = VertexCodeBisonAI()
    print(vertex("python codes to print hello world"))