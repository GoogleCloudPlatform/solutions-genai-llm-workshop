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
import json
import re
from typing import List, Union

from langchain.agents import AgentOutputParser
from langchain.agents.conversational_chat.prompt import FORMAT_INSTRUCTIONS as CHAT_FORMAT_INSTRUCTIONS
from langchain.schema import AgentAction, AgentFinish


class VertexLLMOutputParser(AgentOutputParser):
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        print("***** VertexLLMOutputParser::parse()::llm_output->{}".format(llm_output))
        # If we have the final answer
        if "Final Answer:" in llm_output:
            return AgentFinish(
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        # The output should be in the following format
        # Action: "action name"
        # Action Input: "inputs"
        # Sometimes the LLM may produce Action Input without double quotes
        # We need to handle this.
        regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input:$"
        match = re.search(regex, llm_output, re.DOTALL)
        if match:
            llm_output = llm_output + "\"\""

        regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse LLM output: `{llm_output}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        return AgentAction(
            tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output
        )


def replace_quotes(text):
    import re

    pattern = r"\"action_input\": \"(.*?)\"$"
    match = re.search(pattern=pattern, string=text, flags=re.MULTILINE)
    if match:
        # Print the first (and only) captured group
        print(match.group(1))
        for group in match.groups():
            new_s = group.replace('"', "*")
            text = text.replace(group, new_s)
    return text


class VertexLLMChatOutputParser(AgentOutputParser):
    def get_format_instructions(self) -> str:
        return CHAT_FORMAT_INSTRUCTIONS

    # replacing the first inner quote in action_input field
    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        cleaned_output = text.strip()
        cleaned_output = cleaned_output.strip("AI:")
        if "```json" in cleaned_output:
            _, cleaned_output = cleaned_output.split("```json")
        if "```" in cleaned_output:
            cleaned_output, _ = cleaned_output.split("```")
        if cleaned_output.startswith("```json"):
            cleaned_output = cleaned_output[len("```json") :]
        if cleaned_output.startswith("```"):
            cleaned_output = cleaned_output[len("```") :]
        if cleaned_output.endswith("```"):
            cleaned_output = cleaned_output[: -len("```")]
        cleaned_output = cleaned_output.strip()
        if cleaned_output == "":
            cleaned_output = """
            {"action":"", "action_input":""}
            """
        new_cleaned_output = replace_quotes(text=cleaned_output)
        print(f"***new_cleaned_output={new_cleaned_output}")
        response = json.loads(new_cleaned_output)
        action, action_input = response["action"], response["action_input"]
        if action == "Final Answer":
            return AgentFinish({"output": action_input}, text)
        else:
            return AgentAction(action, action_input, text)
