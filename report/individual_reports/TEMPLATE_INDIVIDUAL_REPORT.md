## I. Technical Contribution

I implemented the ReAct Agent loop in `src/agent/agent.py`. My contribution included action parsing, tool execution, observation feedback, max-step control, and structured telemetry logging.

The agent supports the following workflow:

1. Receive user input.
2. Ask the LLM to produce a `Thought` and `Action`.
3. Parse the action using a regular expression.
4. Execute the selected tool.
5. Append the tool result as an `Observation`.
6. Continue until the LLM returns `Final Answer`.

I also created two tools for testing:

- `calculator`: used for arithmetic and tax calculation.
- `policy_lookup`: used to retrieve predefined company policy information.

## II. Debugging Case Study

Problem: The chatbot baseline could not answer the refund policy question with specific information. It responded with a generic explanation and asked for more details about the company.

Log evidence from the agent run showed that the ReAct Agent solved this limitation:

`Action: policy_lookup(refund)`

The observation returned:

`Customers can request a refund within 30 days if they provide a valid receipt.`

Diagnosis: The baseline chatbot had no access to company-specific data. This was not a model reasoning issue, but a missing tool/data access issue.

Solution: I added the `policy_lookup` tool and allowed the ReAct Agent to call it during the reasoning loop. This grounded the final answer in an explicit tool observation.

## III. Personal Insights: Chatbot vs ReAct Agent

The main difference I observed is that a chatbot answers directly, while a ReAct Agent can break the task into smaller steps. The `Thought` block helps the model decide what action is needed, and the `Observation` gives feedback from the environment before the final answer.

For simple arithmetic, both chatbot and agent can answer correctly. However, the agent is more transparent because the log shows exactly which tool was used and what result was returned.

The agent can be worse than a chatbot when the task is very simple because it uses more tokens and may require multiple LLM calls. In this lab, the agent used 1527 total tokens while the chatbot used 412. This shows a trade-off between reliability and cost.

## IV. Future Improvements

To scale this system toward production, I would add stronger guardrails for tool arguments, better JSON-based action parsing, and retry logic when the model produces an invalid format.

For larger systems, I would connect the agent to a RAG pipeline with a vector database so it can retrieve real company documents instead of using a small dictionary. I would also add monitoring for cost, latency, success rate, parser errors, hallucinated tools, and max-step failures.