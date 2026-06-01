import os
from dotenv import load_dotenv
from src.core.openai_provider import OpenAIProvider
from src.agent.agent import ReActAgent
from src.tools.ecommerce_tools import get_tools_v1

load_dotenv()

llm = OpenAIProvider(
    model_name=os.getenv("DEFAULT_MODEL", "gpt-4o"),
    api_key=os.getenv("OPENAI_API_KEY")
)

agent = ReActAgent(
    llm=llm,
    tools=get_tools_v1(),
    max_steps=6
)

questions = [
    "I want to buy 2 standing desks using coupon OFFICE10 and ship to Danang. What is the total price?",
    "Can I buy 2 portable projectors using coupon BULK15 and ship to Hanoi?",
    "Compare the total cost of buying 1 ergonomic chair shipped to HCMC versus Can Tho.",
    "What discount does coupon WELCOME5 provide?",
    "I want to buy 1 whiteboard using coupon OFFICE10 and ship to Hanoi. What is the total price?"
]

for i, question in enumerate(questions, start=1):
    print("=" * 80)
    print(f"AGENT V1 CASE {i}")
    print("Question:", question)
    print("Answer:", agent.run(question))