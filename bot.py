import os
import requests
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
from ai_agent import app_agent
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_KEY")

# Simple background HTTP server for Render port binding
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive and running!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

def force_takeover():
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=True"
        requests.get(url, timeout=10)
    except Exception as e:
        print(f"Webhook reset notice: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    chat_id = str(update.message.chat_id)
    config = {"configurable": {"thread_id": chat_id}}

    try:
        response = app_agent.invoke(
            {"messages": [HumanMessage(content=user_text)]},
            config=config
        )
        ai_reply = response["messages"][-1].content
        await update.message.reply_text(ai_reply)
    except Exception as e:
        print(f"Error handling message: {e}")
        await update.message.reply_text("Sorry, kuch issue aa gaya. Please thodi der baad try karein.")

if __name__ == "__main__":
    force_takeover()

    # Start background web server for Render Web Service compliance
    threading.Thread(target=run_dummy_server, daemon=True).start()

    print("Starting Telegram Bot with Network Resiliency...")

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