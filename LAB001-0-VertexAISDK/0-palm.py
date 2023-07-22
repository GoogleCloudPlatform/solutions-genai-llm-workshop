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

import vertexai
from vertexai.preview.language_models import TextGenerationModel

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
REGION = os.getenv("GOOGLE_CLOUD_REGIN")
vertexai.init(project=PROJECT_ID, location=REGION)
t = TextGenerationModel.from_pretrained(model_name="text-bison")

print("* hi, what's your name?")
print(t.predict("hi, what's your name?"))

print("* apples are red, banana is:")
print(t.predict("apples are red, banana is:"))

print(
    "* you are a teacher teaches kids, answer the following question in a funny way. apples are red, banana is:"
)
print(
    t.predict(
        """
you are a teacher teaches kids, answer the following question in a funny way.

apples are red, banana is:
"""
    )
)
