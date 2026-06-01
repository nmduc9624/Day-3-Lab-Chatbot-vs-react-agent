import os
from dotenv import load_dotenv
from src.core.openai_provider import OpenAIProvider
from src.agent.agent import ReActAgent

load_dotenv()


def calculator(expression: str) -> str:
    allowed = "0123456789+-*/(). %"
    if not all(ch in allowed for ch in expression):
        raise ValueError("Expression contains unsupported characters.")

    expression = expression.replace("%", "/100")
    return eval(expression, {"__builtins__": {}})


def policy_lookup(topic: str) -> str:
    policies = {
        "refund": "Customers can request a refund within 30 days if they provide a valid receipt.",
        "shipping": "Standard shipping takes 3 to 5 business days.",
        "warranty": "Products include a 12-month warranty for manufacturing defects."
    }

    topic = topic.lower().strip()
    return policies.get(topic, "No policy found for that topic.")


tools = [
    {
        "name": "calculator",
        "description": "Calculate math expressions. Input example: calculator(240 * 15%)",
        "func": calculator
    },
    {
        "name": "policy_lookup",
        "description": "Look up company policy. Input examples: policy_lookup(refund), policy_lookup(shipping), policy_lookup(warranty)",
        "func": policy_lookup
    }
]

llm = OpenAIProvider(
    model_name=os.getenv("DEFAULT_MODEL", "gpt-4o"),
    api_key=os.getenv("OPENAI_API_KEY")
)

agent = ReActAgent(llm=llm, tools=tools, max_steps=5)

questions = [
    "What is 15% tax on 240?",
    "What is the refund policy?",
    "If the product costs 240 and tax is 15%, what is the final price?"
]

for question in questions:
    print("=" * 80)
    print("Question:", question)
    print("Agent answer:", agent.run(question))