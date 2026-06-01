# Individual Report: Lab 3 - Agent v2 Improvement and Interactive Demo

- **Student Name**: Nguyễn Đoàn Gia Tuấn    
- **Student ID**: 2A202600669
- **Date**: 2026-06-01
- **Role**: Agent v2 improvement, tool design evolution, expanded database, CLI chat, and UI demo

---

## I. Technical Contribution

My role in the group was to continue after Agent v1, analyze the failure traces, and build Agent v2. This work was sequentially dependent on Member 1's baseline and Agent v1 results because Agent v2 was designed from the actual errors found in the logs.

I improved the ReAct Agent by updating the tool descriptions and system prompt in `src/agent/agent.py`. The improved prompt tells the agent to follow the exact `Thought -> Action -> Observation -> Final Answer` format, use only available tools, check stock before purchase calculations, and calculate shipping using product weight and shipping rate.

I also improved the toolset in `src/tools/ecommerce_tools.py`. Agent v2 includes:

- `get_weight`: added to calculate shipping correctly.
- `list_products`: lists all products in the catalog.
- `search_catalog`: searches products by name, category, or related keyword.
- `suggest_alternatives`: recommends available alternatives when the requested item is missing.
- `draw_order_flow`: returns an ASCII workflow diagram for the order calculation process.

In addition, I expanded the procurement database with more realistic office products such as:

- `business smartphone`
- `voip desk phone`
- `4k monitor`
- `laser printer`
- `mesh wifi router`
- `ups battery backup`
- `whiteboard`

I also created an interactive interface so users can ask their own questions instead of only running fixed test cases:

- `chat_cli.py`: command-line chat interface.
- `app.py`: browser UI with a responder selector for `Chatbot baseline`, `Agent v1`, and `Agent v2`.

This allows the group to compare all three systems using the same user question.

---

## II. Debugging Case Study

The main failure used to design Agent v2 came from Agent v1's inability to complete multi-step calculations within the step limit.

**Problem**

Agent v1 failed on the standing desk task:

```text
I want to buy 2 standing desks using coupon OFFICE10 and ship to Danang. What is the total price?
```

It gathered all required facts but stopped with:

```text
AGENT_END -> status: max_steps_exceeded
```

**Diagnosis**

The trace showed that Agent v1 called the correct tools but did not complete the final arithmetic. The key missing part was a compact final calculation that included product subtotal, discount, product weight, and shipping rate.

The correct formula should be:

```text
final_total = (quantity * unit_price) * (1 - discount_rate) + (quantity * product_weight * shipping_rate)
```

For the standing desk case:

```text
(2 * 320) * (1 - 0.10) + (2 * 28.0 * 6) = 912
```

**Solution**

In Agent v2, I improved the prompt and tool descriptions so the model knows to:

1. Call `check_stock(product)`.
2. Call `get_price(product)`.
3. Call `get_discount(coupon)`.
4. Call `get_weight(product)`.
5. Call `calc_shipping(destination)`.
6. Call `calculator(...)` with the complete final expression.

The Agent v2 trace confirmed the fix:

```text
check_stock(standing desk) -> 4 units
get_price(standing desk) -> 320 USD
get_discount(OFFICE10) -> 10%
get_weight(standing desk) -> 28.0 kg
calc_shipping(Danang) -> 6 USD/kg
calculator(((320 * 2) * (1 - 0.10)) + (2 * 28.0 * 6)) -> 912.0
Final Answer: 912 USD
```

Agent v2 completed the final evaluated set with 5/5 successful answers and no max-step failures in the final run.

---

## III. Personal Insights: Chatbot vs ReAct Agent

The biggest difference I observed is that a chatbot explains, while an agent can act. The chatbot baseline produced fluent answers, but it did not know the product database, coupon values, stock quantity, product weights, or shipping rates. It often asked the user to provide the missing data.

Agent v1 demonstrated the value of tool use, but also showed that a weak agent can still fail. It had access to tools but could run out of steps or generate an invalid action. This helped me understand that agent quality depends on prompt design, tool descriptions, parser behavior, and observability.

Agent v2 was more reliable because its answers were grounded in tool observations. The logs made the final answer auditable: each number in the answer came from a tool call. However, Agent v2 also used more tokens and latency than the chatbot because it required multiple LLM calls and tool interactions.

My main insight is that ReAct Agents are best for tasks where correctness depends on external data and multi-step reasoning. For very simple questions, a chatbot may be cheaper and faster. For operational workflows, an agent is more reliable and easier to debug.

---

## IV. Future Improvements

To improve this system further, I would:

- Replace regex-based action parsing with structured JSON tool calls.
- Add Pydantic validation for each tool's input.
- Add automatic retries when the model returns more than one action in a single response.
- Store products, coupons, and shipping rates in a real database.
- Add a log parser that automatically calculates success rate, token count, latency, tool errors, and max-step failures.
- Improve the UI with side-by-side comparison of Chatbot, Agent v1, and Agent v2 answers.
- Add authentication and role-based user management if the demo becomes a deployed web app.

The most valuable next step would be to make the tool interface stricter. This would reduce parser errors and make the agent more production-ready.
