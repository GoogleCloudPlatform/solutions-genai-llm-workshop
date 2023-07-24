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
from langchain.tools import BaseTool
from langchain.tools.base import tool


class MockTool(BaseTool):
    name = "MockTool"
    description = "useful for when you need to answer questions about a person"

    def _run(self, query: str) -> str:
        """Use the tool."""
        print(f"*** Invoking MockTool with query '{query}'")
        return f"Answer of '{query}' is 'Michael Chi'"

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        print(f"*** Invoking MockTool with query '{query}'")
        return f"Answer of '{query}' is 'Michael Chi'"


# return_direct=True | False
@tool("MockTool_Function", return_direct=False)
def MockTool_Function(query: str) -> str:
    """
    useful for when you need to answer questions about everything about Google PaLM2
    """
    print(f">MockTool_Functioon says {query}")
    return """
PaLM 2 is our next generation large language model that builds on Google’s legacy
of breakthrough research in machine learning and responsible AI.
It excels at advanced reasoning tasks, including code and math,
classification and question answering, translation and multilingual proficiency,
and natural language generation better than our previous state-of-the-art LLMs,
including PaLM. It can accomplish these tasks because of the way it was built
– bringing together compute-optimal scaling, an improved dataset mixture,
and model architecture improvements.
PaLM 2 is grounded in Google’s approach to building and deploying AI responsibly.
It was evaluated rigorously for its potential harms and biases,
capabilities and downstream uses in research and in-product applications.

It’s being used in other state-of-the-art models, like Med-PaLM 2 and Sec-PaLM,
and is powering generative AI features and tools at Google,
like Bard and the PaLM API.
"""


@tool("MockTool_Function_Return_Direct", return_direct=True)
def MockTool_Function_Return_Direct(query: str) -> str:
    """
    useful for when you need to answer questions about everything about Google Bard
    """
    return """
Bard is an experiment based on this same technology that lets you collaborate with generative AI.
As a creative and helpful collaborator, Bard can supercharge your imagination, boost your productivity,
and help you bring your ideas to life.

If you’re interested in the more technical details, LaMDA is a Transformer-based model,
the machine-learning breakthrough invented by Google in 2017Opens in a new window.

The language model learns by “reading” trillions of words that help it pick up on patterns that make up human language,
so it’s good at predicting what might be reasonable responses.
"""
