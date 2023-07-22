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
from langchain.llms.vertexai import VertexAI

llm = VertexAI(temperature=0.2, top_p=1, top_k=40)

text = "* hello, I am Michael, what's your name ?"
print(f"{text}")
response = llm(text)
print(response)

text = "* why is the sky blue？"
print(f"{text}")
response = llm(text)
print(response)
