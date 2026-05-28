#!/usr/bin/env python3
"""
بوت تليجرام مدعوم بـ Google Gemini
"""

import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ══════════════════════════════════════════
#  إعدادات البوت
# ══════════════════════════════════════════
TELEGRAM_TOKEN = "8657095276:AAEVFG6dvxem5BPbUQO8Q7ZryVUwbCaGEAA"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# تخزين محادثات المستخدمين
user_conversations: dict[int, list] = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"أهلاً وسهلاً {user.first_name}! 👋\n\n"
        "أنا بوت ذكاء اصطناعي مدعوم بـ Google Gemini.\n"
        "اسألني أي شيء وسأجيبك! 🤖\n\n"
        "الأوامر المتاحة:\n"
        "• /start - بدء المحادثة\n"
        "• /clear - مسح سجل المحادثة\n"
        "• /help - المساعدة"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆘 المساعدة\n\n"
        "فقط أرسل أي سؤال أو رسالة وسأرد عليك!\n\n"
        "الأوامر:\n"
        "• /start - بدء المحادثة\n"
        "• /clear - مسح سجل المحادثة\n"
        "• /help - عرض هذه الرسالة"
    )

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_conversations[user_id] = []
    await update.message.reply_text("✅ تم مسح سجل المحادثة! ابدأ من جديد.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text

    await update.message.chat.send_action("typing")

    if user_id not in user_conversations:
        user_conversations[user_id] = []

    user_conversations[user_id].append({
        "role": "user",
        "parts": [user_message]
    })

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="أنت مساعد ذكاء اصطناعي مفيد وودود. أجب بنفس لغة المستخدم. كن مختصراً ومفيداً."
        )

        chat = model.start_chat(history=user_conversations[user_id][:-1])
        response = chat.send_message(user_message)
        assistant_reply = response.text

        user_conversations[user_id].append({
            "role": "model",
            "parts": [assistant_reply]
        })

        if len(user_conversations[user_id]) > 20:
            user_conversations[user_id] = user_conversations[user_id][-20:]

        await update.message.reply_text(assistant_reply)

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("⚠️ حدث خطأ. حاول مرة أخرى.")

def main():
    if not GEMINI_API_KEY:
        print("⚠️ تحذير: لم يتم تعيين GEMINI_API_KEY")

    print("🤖 جاري تشغيل البوت...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ البوت يعمل الآن!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()