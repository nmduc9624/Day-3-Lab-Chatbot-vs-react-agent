import re
from typing import List, Dict, Any
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger


class ReActAgent:
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps

    def get_system_prompt(self) -> str:
        tool_descriptions = "\n".join(
            [f"- {t['name']}: {t['description']}" for t in self.tools]
        )

        return f"""
You are a ReAct agent. You can reason step by step and use tools.

Available tools:
{tool_descriptions}

Use exactly this format:

Thought: explain what you need to do.
Action: tool_name(argument)

After receiving an Observation, continue reasoning.

When you know the answer, respond with:

Final Answer: your final answer.

Rules:
- Use tools when calculation or lookup is needed.
- Do not invent tool names.
- Use only one Action per step.
"""

    def run(self, user_input: str) -> str:
        logger.log_event("AGENT_START", {
            "input": user_input,
            "model": self.llm.model_name
        })

        scratchpad = f"User question: {user_input}\n"
        system_prompt = self.get_system_prompt()

        for step in range(1, self.max_steps + 1):
            result = self.llm.generate(scratchpad, system_prompt=system_prompt)
            content = result["content"]

            logger.log_event("LLM_RESPONSE", {
                "step": step,
                "content": content,
                "usage": result.get("usage", {}),
                "latency_ms": result.get("latency_ms")
            })

            if "Final Answer:" in content:
                final_answer = content.split("Final Answer:", 1)[1].strip()
                logger.log_event("AGENT_END", {
                    "status": "success",
                    "steps": step,
                    "answer": final_answer
                })
                return final_answer

            action_match = re.search(r"Action:\s*([a-zA-Z_][a-zA-Z0-9_]*)\((.*)\)", content)

            if not action_match:
                logger.log_event("PARSER_ERROR", {
                    "step": step,
                    "content": content
                })
                scratchpad += f"\nAssistant response:\n{content}\nObservation: Parser error. Use Action: tool_name(argument) or Final Answer.\n"
                continue

            tool_name = action_match.group(1)
            args = action_match.group(2).strip().strip('"').strip("'")

            observation = self._execute_tool(tool_name, args)

            logger.log_event("TOOL_CALL", {
                "step": step,
                "tool": tool_name,
                "args": args,
                "observation": observation
            })

            scratchpad += f"""
Assistant response:
{content}
Observation: {observation}
"""

        logger.log_event("AGENT_END", {
            "status": "max_steps_exceeded",
            "steps": self.max_steps
        })

        return "The agent could not finish within the maximum number of steps."

    def _execute_tool(self, tool_name: str, args: str) -> str:
        for tool in self.tools:
            if tool["name"] == tool_name:
                try:
                    return str(tool["func"](args))
                except Exception as e:
                    return f"Tool error: {e}"

        return f"Tool {tool_name} not found."