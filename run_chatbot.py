import os
from dotenv import load_dotenv
from src.core.openai_provider import OpenAIProvider

load_dotenv()

llm = OpenAIProvider(
    model_name=os.getenv("DEFAULT_MODEL", "gpt-4o"),
    api_key=os.getenv("OPENAI_API_KEY")
)

questions = [
    "What is 15% tax on 240?",
    "What is the refund policy?",
    "If the product costs 240 and tax is 15%, what is the final price?"
]

for question in questions:
    result = llm.generate(question)
    print("=" * 80)
    print("Question:", question)
    print("Chatbot answer:", result["content"])
    print("Usage:", result["usage"])
    print("Latency:", result["latency_ms"], "ms")