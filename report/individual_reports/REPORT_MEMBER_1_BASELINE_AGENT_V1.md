# Individual Report: Lab 3 - Chatbot Baseline and Agent v1

- **Student Name**: [Member 1 Name]
- **Student ID**: [Member 1 ID]
- **Date**: 2026-06-01
- **Role**: Chatbot baseline, initial tool design, Agent v1 testing, and failure trace collection

---

## I. Technical Contribution

My role in the group was to build the first half of the lab workflow: chatbot baseline, initial procurement tools, Agent v1 execution, and log collection for failure analysis.

I implemented and tested the chatbot baseline in `run_chatbot.py`. This baseline used OpenAI `gpt-4o` directly without tools, observations, or action execution. I used it to show that a normal chatbot can explain the calculation process, but cannot access structured product data such as stock, price, coupon value, product weight, or shipping rate.

I also helped define the first version of the Smart Office Procurement dataset and tools in `src/tools/ecommerce_tools.py`. The initial toolset included:

- `check_stock`: check product availability.
- `get_price`: retrieve product unit price.
- `get_weight`: retrieve product weight for shipping.
- `get_discount`: retrieve coupon discount percentage.
- `calc_shipping`: retrieve shipping rate by destination.
- `calculator`: calculate arithmetic expressions.

For Agent v1, I ran the shared test set:

1. Buy 2 standing desks with `OFFICE10` and ship to Danang.
2. Buy 2 portable projectors with `BULK15` and ship to Hanoi.
3. Compare 1 ergonomic chair shipped to HCMC versus Can Tho.
4. Check the discount for `WELCOME5`.
5. Buy 1 whiteboard with `OFFICE10` and ship to Hanoi.

My contribution produced the first set of logs used by the group to identify weaknesses in Agent v1 and decide how Agent v2 should be improved.

---

## II. Debugging Case Study

The most important Agent v1 failure happened in the multi-step standing desk order.

**Problem**

Agent v1 collected the correct data but did not finish the final calculation before reaching the maximum step limit.

**Log Evidence**

For the input:

```text
I want to buy 2 standing desks using coupon OFFICE10 and ship to Danang. What is the total price?
```

Agent v1 produced this trace:

```text
check_stock(standing desk) -> standing desk stock: 4 units.
get_price(standing desk) -> standing desk price: 320 USD.
get_discount(OFFICE10) -> OFFICE10 discount: 10%.
get_weight(standing desk) -> standing desk weight: 28.0 kg.
calc_shipping(Danang) -> Shipping rate to Danang: 6 USD per kg.
calculator(2 * 320) -> 640
AGENT_END -> status: max_steps_exceeded
```

**Diagnosis**

Agent v1 needed more reasoning steps than the configured `max_steps=6`. It correctly gathered stock, price, discount, weight, and shipping rate, but only calculated the product subtotal before the loop ended. The agent did not complete the discount calculation, shipping calculation, and final total.

This was not a data problem. The tools returned useful observations. The failure came from the agent loop configuration and the fact that the model was using too many small reasoning steps.

**Solution**

This trace was passed to the Agent v2 work. The next version increased the step budget and improved tool instructions so the agent could combine the final arithmetic into one calculator call:

```text
calculator(((320 * 2) * (1 - 0.10)) + (2 * 28.0 * 6)) -> 912.0
```

This fixed the max-step failure for the same task.

---

## III. Personal Insights: Chatbot vs ReAct Agent

The chatbot baseline was useful as a comparison point because it showed the limitation of direct LLM answers. For every procurement task, the chatbot answered fluently but asked for missing information such as product price, coupon value, and shipping cost. It could explain a formula, but it could not ground its answer in the project database.

Agent v1 was already more useful because it could act. It checked stock, retrieved prices, looked up coupons, and used a calculator. However, Agent v1 also showed that having tools is not enough. The agent must use tools in the right sequence, respect the action format, and have enough loop budget to finish.

The most important lesson I learned is that the trace is the real debugging artifact. The final answer alone does not explain why the agent failed. The JSON logs showed exactly where the process stopped and which observation was available at each step.

---

## IV. Future Improvements

For future versions, I would improve Agent v1 in these ways:

- Track token count, latency, tool calls, and step count automatically per test case.
- Add a stricter one-action-per-step parser.
- Add automatic detection for `max_steps_exceeded`.
- Add a summary script that reads JSON logs and calculates success rate.
- Keep chatbot baseline and Agent v1 test cases identical so comparisons remain fair.

In a production system, I would also move product, coupon, and shipping data from Python dictionaries into a real database or API so the tools can scale beyond a small lab dataset.
