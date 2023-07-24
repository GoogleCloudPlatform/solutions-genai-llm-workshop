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
from typing import List

from langchain.embeddings import VertexAIEmbeddings
from langchain.embeddings.base import Embeddings


class MyVertexAIEmbedding(VertexAIEmbeddings, Embeddings):
    model_name: str = "textembedding-gecko"
    max_batch_sizes: int = 5

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of strings.

        Args:
            texts: List[str] The list of strings to embed.

        Returns:
            List of embeddings, one for each text.
        """
        chunked_texts = [
            texts[i : i + self.max_batch_sizes]
            for i in range(0, len(texts), self.max_batch_sizes)
        ]
        embeddings = []

        for chunk in chunked_texts:
            embeddings.extend(self.client.get_embeddings(chunk))

        return [el.values for el in embeddings]

    def embed_query(self, text: str) -> List[float]:
        """Embed a text.

        Args:
            text: The text to embed.

        Returns:
            Embedding for the text.
        """
        embeddings = self.client.get_embeddings([text])
        return embeddings[0].values
