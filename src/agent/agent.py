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
            [f"- {tool['name']}: {tool['description']}" for tool in self.tools]
        )

        tool_names = ", ".join([tool["name"] for tool in self.tools])

        return f"""
You are a ReAct agent for a smart e-commerce assistant.

Available tools:
{tool_descriptions}

Allowed tool names:
{tool_names}

Use exactly this format when calling a tool:

Thought: explain the next step.
Action: tool_name(argument)

After receiving an Observation, continue reasoning.

When you know the answer, respond with:

Final Answer: your final answer.

Important rules:
- Use only tools listed in Allowed tool names.
- Use only one Action per step.
- Do not invent tool names.
- Follow each tool's input format exactly.
- For purchase questions, check stock before calculating the final price.
- For shipping, first call get_weight with product name only, for example: get_weight(standing desk).
- Then call calc_shipping with destination city only, for example: calc_shipping(Hanoi).
- Shipping cost formula is quantity * product_weight_kg * shipping_rate_per_kg.
- Do not pass product name to calc_shipping.
- For coupon discount, call get_discount with coupon code only, for example: get_discount(WINNER).
- If a product is unknown or not found, call search_catalog or list_products before the Final Answer.`r`n- If there is no exact product match, call suggest_alternatives and offer available alternatives.`r`n- If the user asks to draw, visualize, or show the workflow, call draw_order_flow.`r`n- If a coupon is not found, explain the issue and mention available coupon information when provided by the tool.
- Use calculator for arithmetic after collecting price, discount, product weight, and shipping rate.
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

            action_match = re.search(
                r"Action:\s*([a-zA-Z_][a-zA-Z0-9_]*)\((.*)\)",
                content,
                flags=re.DOTALL
            )

            if not action_match:
                logger.log_event("PARSER_ERROR", {
                    "step": step,
                    "content": content
                })
                scratchpad += (
                    f"\nAssistant response:\n{content}\n"
                    "Observation: Parser error. Please use Action: tool_name(argument) or Final Answer.\n"
                )
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

