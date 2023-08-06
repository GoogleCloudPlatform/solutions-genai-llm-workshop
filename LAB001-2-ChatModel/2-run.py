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
from litellm import completion
messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant that translates English to Japanese."
    },
    {
        "role": "user",
        "content": "I am Michael, how are you."
    }
]
# google palm call
result = completion(model="chat-bison-001", messages=messages)

# google palm bison001 call
result = completion(model="text-bison-001", messages=messages)

# openai call
result = completion(model="gpt-3.5-turbo", messages=messages)

# command nightly call
result = completion(model="command-nightly", messages=messages)

# claude call
result = completion(model="claude-v2", messages=messages)

