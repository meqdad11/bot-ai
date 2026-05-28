import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = "8657095276:AAEVFG6dvxem5BPbUQO8Q7ZryVUwbCaGEAA"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

user_chats = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"أهلاً {update.effective_user.first_name}! 👋\n"
        "أنا بوت ذكاء اصطناعي مدعوم بـ Gemini 🤖\n"
        "اسألني أي شيء!\n/clear - مسح المحادثة"
    )

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_chats.pop(update.effective_user.id, None)
    await update.message.reply_text("✅ تم مسح المحادثة!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    msg = update.message.text
    await update.message.chat.send_action("typing")
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        if user_id not in user_chats:
            user_chats[user_id] = model.start_chat(history=[])
        response = user_chats[user_id].send_message(msg)
        await update.message.reply_text(response.text)
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("⚠️ حدث خطأ، حاول مرة أخرى.")

def main():
    print("🤖 البوت يعمل...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()