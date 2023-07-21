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
from langchain.chat_models import ChatVertexAI
from langchain.schema import HumanMessage, SystemMessage

chat = ChatVertexAI()

messages = [
    SystemMessage(
        content="You are a helpful assistant that translates English to Japanese."
    ),
    HumanMessage(content="I am Michael, how are you."),
]
res = chat(messages)
print(res.content)
messages.extend([res])

messages.extend([HumanMessage(content="what's your name.")])
res = chat(messages)
print(res.content)
messages.extend([res])

print(
    f"""
===
{messages}
===
"""
)

messages.extend([HumanMessage(content="say my name again.")])
res = chat(messages)
print(res.content)
messages.extend([res])
