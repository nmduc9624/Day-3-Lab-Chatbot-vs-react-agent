import os
from dotenv import load_dotenv
from src.agent.agent import ReActAgent
from src.core.openai_provider import OpenAIProvider
from src.tools.ecommerce_tools import get_tools_v1, get_tools_v2

load_dotenv()


def build_llm() -> OpenAIProvider:
    return OpenAIProvider(
        model_name=os.getenv("DEFAULT_MODEL", "gpt-4o"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )


def build_responders():
    llm = build_llm()
    return {
        "chatbot": {
            "label": "Chatbot baseline",
            "answer": lambda question: llm.generate(question)["content"],
        },
        "agentv1": {
            "label": "Agent v1",
            "answer": ReActAgent(llm=llm, tools=get_tools_v1(), max_steps=6).run,
        },
        "agentv2": {
            "label": "Agent v2",
            "answer": ReActAgent(llm=llm, tools=get_tools_v2(), max_steps=10).run,
        },
    }


def choose_mode():
    print("Choose who will answer:")
    print("1. Chatbot baseline")
    print("2. Agent v1")
    print("3. Agent v2")
    choice = input("Mode [1/2/3]: ").strip()
    return {"1": "chatbot", "2": "agentv1", "3": "agentv2"}.get(choice, "agentv2")


def main():
    responders = build_responders()
    mode = choose_mode()

    print("\nSmart Office Procurement Lab Chat")
    print("Commands: /mode chatbot | /mode agentv1 | /mode agentv2 | /who | exit\n")

    while True:
        question = input(f"You [{responders[mode]['label']}]: ").strip()
        if question.lower() in {"exit", "quit", "q"}:
            print("Goodbye.")
            break
        if not question:
            continue
        if question.lower() == "/who":
            print(f"Current responder: {responders[mode]['label']}\n")
            continue
        if question.lower().startswith("/mode "):
            requested = question.split(maxsplit=1)[1].strip().lower()
            aliases = {
                "chatbot": "chatbot", "baseline": "chatbot",
                "agent1": "agentv1", "agentv1": "agentv1", "v1": "agentv1",
                "agent2": "agentv2", "agentv2": "agentv2", "v2": "agentv2",
            }
            if requested in aliases:
                mode = aliases[requested]
                print(f"Switched to: {responders[mode]['label']}\n")
            else:
                print("Unknown mode. Use chatbot, agentv1, or agentv2.\n")
            continue

        answer = responders[mode]["answer"](question)
        print(f"{responders[mode]['label']}: {answer}\n")


if __name__ == "__main__":
    main()
