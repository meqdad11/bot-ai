#!/usr/bin/env python3
import os
import logging
from google import genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = "8657095276:AAEVFG6dvxem5BPbUQO8Q7ZryVUwbCaGEAA"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

user_conversations: dict[int, list] = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"أهلاً {user.first_name}! 👋\n"
        "أنا بوت ذكاء اصطناعي مدعوم بـ Gemini 🤖\n"
        "اسألني أي شيء!\n\n"
        "/clear - مسح المحادثة\n"
        "/help - المساعدة"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل أي سؤال وسأرد عليك!\n/clear - مسح سجل المحادثة")

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_conversations[update.effective_user.id] = []
    await update.message.reply_text("✅ تم مسح المحادثة!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    await update.message.chat.send_action("typing")

    if user_id not in user_conversations:
        user_conversations[user_id] = []

    user_conversations[user_id].append({"role": "user", "parts": [{"text": user_message}]})

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=user_conversations[user_id],
            config=genai.types.GenerateContentConfig(
                system_instruction="أنت مساعد ذكاء اصطناعي مفيد. أجب بنفس لغة المستخدم. كن مختصراً ومفيداً."
            )
        )
        reply = response.text
        user_conversations[user_id].append({"role": "model", "parts": [{"text": reply}]})
        if len(user_conversations[user_id]) > 20:
            user_conversations[user_id] = user_conversations[user_id][-20:]
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("⚠️ حدث خطأ. حاول مرة أخرى.")

def main():
    print("🤖 جاري تشغيل البوت...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ البوت يعمل!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()