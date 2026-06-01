## 1. Executive Summary

In this lab, our team implemented and evaluated a ReAct Agent using OpenAI `gpt-4o`. The goal was to compare a normal chatbot baseline with an agentic system that can reason step by step and call tools.

The ReAct Agent achieved a 100% success rate on 3 test cases. Compared with the chatbot baseline, the agent produced more traceable and reliable answers because each reasoning step was connected to a tool call and an observation. The strongest improvement appeared in the refund policy question: the chatbot gave a generic answer, while the agent used `policy_lookup(refund)` and returned the exact policy.

## 2. System Architecture & Tooling

The agent follows the ReAct loop:

Thought -> Action -> Observation -> Final Answer

At each step, the LLM decides whether it needs to call a tool. If an action is detected, the system parses the tool name and arguments, executes the tool, logs the observation, and sends the updated scratchpad back to the LLM. The process stops when the model returns `Final Answer`.

| Tool Name | Input Format | Use Case |
| :--- | :--- | :--- |
| `calculator` | math expression string | Calculate tax, totals, and arithmetic expressions |
| `policy_lookup` | policy topic string | Retrieve predefined company policy such as refund, shipping, or warranty |

Primary provider: OpenAI  
Model used: `gpt-4o`

## 3. Telemetry & Performance Dashboard

The system logs structured JSON events including `AGENT_START`, `LLM_RESPONSE`, `TOOL_CALL`, and `AGENT_END`.

Final run metrics:

- Success Rate: 3/3 test cases
- Average Agent Steps: 2.33 steps per task
- Total Agent Tokens: 1527
- Average Tokens per Agent Task: 509
- Total Agent Latency: 6548 ms
- Average Agent Latency: 2183 ms
- Parser Errors: 0
- Hallucinated Tool Calls: 0
- Max-step Failures: 0

## 4. Root Cause Analysis / Failure Analysis

No parser error, hallucinated tool, or max-step failure occurred in the final run. However, the baseline chatbot exposed an important reliability limitation. For the question "What is the refund policy?", the chatbot could not access the company policy data and therefore gave a generic answer asking for more context.

Root cause: the chatbot has no external tool or data source. It can only rely on general language knowledge.

Solution: the ReAct Agent was connected to `policy_lookup`, allowing it to retrieve a specific observation before producing the final answer.

## 5. Chatbot vs Agent Insight

The chatbot was faster to implement and worked well for simple arithmetic. However, its answers were not grounded in tool outputs. The ReAct Agent used more tokens because it needed system instructions, reasoning traces, observations, and multiple LLM calls. In return, it produced auditable traces and more reliable answers for tasks requiring calculation or data lookup.