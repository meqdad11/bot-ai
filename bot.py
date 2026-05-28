#!/usr/bin/env python3
"""
بوت تليجرام مدعوم بالذكاء الاصطناعي Claude
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import anthropic

TELEGRAM_TOKEN = "8657095276:AAEVFG6dvxem5BPbUQO8Q7ZryVUwbCaGEAA"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

user_conversations: dict[int, list] = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"أهلاً وسهلاً {user.first_name}! 👋\n\n"
        "أنا بوت ذكاء اصطناعي مدعوم بـ Claude.\n"
        "اسألني أي شيء وسأجيبك! 🤖\n\n"
        "الأوامر المتاحة:\n"
        "• /start - بدء المحادثة\n"
        "• /clear - مسح سجل المحادثة\n"
        "• /help - المساعدة"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆘 *المساعدة*\n\n"
        "فقط أرسل أي سؤال أو رسالة وسأرد عليك!\n\n"
        "الأوامر:\n"
        "• /start - بدء المحادثة\n"
        "• /clear - مسح سجل المحادثة (بداية جديدة)\n"
        "• /help - عرض هذه الرسالة",
        parse_mode="Markdown"
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
    user_conversations[user_id].append({"role": "user", "content": user_message})
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system="أنت مساعد ذكاء اصطناعي مفيد وودود تتحدث العربية والإنجليزية. أجب بنفس لغة المستخدم. كن مختصراً ومفيداً.",
            messages=user_conversations[user_id]
        )
        assistant_reply = response.content[0].text
        user_conversations[user_id].append({"role": "assistant", "content": assistant_reply})
        if len(user_conversations[user_id]) > 20:
            user_conversations[user_id] = user_conversations[user_id][-20:]
        await update.message.reply_text(assistant_reply)
    except anthropic.AuthenticationError:
        await update.message.reply_text("❌ خطأ في مفتاح Anthropic API.")
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("⚠️ حدث خطأ غير متوقع. حاول مرة أخرى.")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
