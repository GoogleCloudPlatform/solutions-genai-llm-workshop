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

urls = ["https://tw.news.yahoo.com/%E5%8F%AA%E6%8E%A5%E5%BE%85%E5%8F%B0%E7%81%A3%E9%81%8A%E5%AE%A2-77%E6%AD%B2%E6%97%A5%E6%9C%AC%E7%88%BA%E7%88%BA-%E5%85%8D%E8%B2%BB-%E7%95%B6%E5%B0%8E%E9%81%8A-%E6%97%A5%E6%9A%A2%E9%81%8A%E4%BC%8A%E8%B1%86%E9%AB%98%E5%8E%9F-091514801.html"]

loader = UnstructuredURLLoader(urls=urls)
documents = loader.load_and_split()
print("===>>>")
print(documents)
print("===<<<")
query = "簡單總結一下這個新聞"
chain = load_qa_chain(llm=llm, chain_type="stuff", verbose=True)
answer = chain.run(input_documents=documents, question=query)
print(answer)
