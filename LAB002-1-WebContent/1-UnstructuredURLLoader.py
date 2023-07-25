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
from langchain.chains.question_answering import load_qa_chain
from langchain.document_loaders import UnstructuredURLLoader
from langchain.llms.vertexai import VertexAI

llm = VertexAI(temperature=0.2, max_output_tokens=1024)

urls = ["https://zh.wikipedia.org/wiki/Bard_(%E8%81%8A%E5%A4%A9%E6%A9%9F%E5%99%A8%E4%BA%BA)"]

loader = UnstructuredURLLoader(urls=urls)
documents = loader.load_and_split()

query = "請用300字簡單描述Bard的發展"
chain = load_qa_chain(llm=llm, chain_type="stuff", verbose=True)
answer = chain.run(input_documents=documents, question=query)
print(answer)
