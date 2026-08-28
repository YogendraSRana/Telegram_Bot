import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
from langchain_core.messages import HumanMessage
from ai_agent import agent

load_dotenv()

TOKEN = os.getenv("TELEGRAM_KEY")

def force_takeover():
    """Pending updates aur old webhook conflicts clear karta hai."""
    try:
        base = f"https://api.telegram.org/bot{TOKEN}"
        requests.post(f"{base}/deleteWebhook", params={"drop_pending_updates": True}, timeout=5)
    except Exception:
        pass

def extract_text(msg):
    c = msg.content
    if isinstance(c, str):
        return c
    parts = [b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text"]
    return "\n".join(p for p in parts if p.strip()) or "(no response)"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    chat_id = str(update.effective_chat.id)

    try:
        result = await agent.ainvoke(
            {"messages": [HumanMessage(content=user_text)]},
            config={"configurable": {"thread_id": chat_id}}
        )
        reply = extract_text(result["messages"][-1])
        await update.message.reply_text(reply)
    except Exception as e:
        print(f"[Error Handled]: {e}")
        # Network retry / fallback
        try:
            await update.message.reply_text("Connection reconnected. Kripya apna message dobara bhejein.")
        except Exception:
            pass

if __name__ == "__main__":
    force_takeover()
    print("Starting Telegram Bot with Network Resiliency...")

    # Network drops aur timeouts ko handle karne ke liye resilient HTTP request config
    request_config = HTTPXRequest(
        connection_pool_size=8,
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=30.0
    )

    app = (
        Application.builder()
        .token(TOKEN)
        .request(request_config)
        .build()
    )

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(drop_pending_updates=True, poll_interval=1.0)