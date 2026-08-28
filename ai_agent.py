import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from tools import get_current_datetime, web_search, get_cricket_score

load_dotenv()

gemini_key = os.getenv("gemini_key") or os.getenv("GOOGLE_API_KEY")

# Purane code wala standard lightweight model
gemini = init_chat_model(
    "google_genai:gemini-3.1-flash-lite",
    api_key=gemini_key
)

tools = [
    get_current_datetime,
    web_search,
    get_cricket_score
]

agent = create_react_agent(
    model=gemini,
    tools=tools,
    checkpointer=InMemorySaver(),
    prompt="You are a smart AI Assistant on Telegram. Always use tools for live queries, dates, or cricket scores. Keep responses concise and direct."
)

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "1"}}
    print("Agent is ready! (Type 'exit' or 'quit' to stop)")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        response = agent.invoke({"messages": [("user", user_input)]}, config=config)
        print(f"Agent: {response['messages'][-1].content}")