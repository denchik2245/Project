import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Введите ваш город и город, который хотите посетить.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Используйте команду /start для начала работы с ботом.")

def start_bot(config: dict) -> None:
    token = config['telegram']['token']
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    logger.info("Бот запущен. Ожидание сообщений...")
    app.run_polling()