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
import re
from typing import List, Union

from langchain.agents import AgentOutputParser, Tool
from langchain.agents.chat.prompt import FORMAT_INSTRUCTIONS
from langchain.prompts import StringPromptTemplate
from langchain.schema import AgentAction, AgentFinish


class VertexPromptTemplate(StringPromptTemplate):
    template: str = """
You are an helpful agent.
Answer the following questions as best you can.
You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question.

Begin!

Question: {input}
{agent_scratchpad}"""
    tools: List[Tool]

    def format(self, **kwargs) -> str:
        intermediate_steps = kwargs.pop("intermediate_steps")
        # This is the first iteration, there is no agent thoughts yet.
        if "agent_scratchpad" not in kwargs:
            kwargs["agent_scratchpad"] = ""
        # Retrieve action and observation of this iteration
        for action, observation in intermediate_steps:
            kwargs["agent_scratchpad"] += action.log
            kwargs["agent_scratchpad"] += f"\nObservation: {observation}\nThought: "
        kwargs["tools"] = "\n".join(
            [f"* {tool.name}: {tool.description}" for tool in self.tools]
        )
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        return self.template.format(**kwargs)


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
