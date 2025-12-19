import logging
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ================== НАСТРОЙКИ ==================

BOT_TOKEN = "8473905923:AAHkAFPuw3klLmhLpNAT21oGqQZzTOReVTM"

ADMIN_CHAT_ID = -1003669017168  # ID группы / чата для обращений

ADMIN_IDS = {1747890756}  # ТВОЙ Telegram ID (можно несколько)

COOLDOWN = timedelta(hours=6)

# ================== ЛОГИ ==================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Храним время последнего обращения пользователей
last_request_time = {}

# ================== ХЕНДЛЕРЫ ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 👋\n"
        "Опиши свою проблему, мы постараемся ответить в ближайшее время."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Бот работает ТОЛЬКО в личке
    if update.message.chat.type != "private":
        return

    user_id = update.message.from_user.id
    now = datetime.now()

    logging.info(f"Сообщение от {user_id}")

    # ================== ПРОВЕРКА ОГРАНИЧЕНИЯ ==================
    if user_id not in ADMIN_IDS:
        if user_id in last_request_time:
            if now - last_request_time[user_id] < COOLDOWN:
                remaining = COOLDOWN - (now - last_request_time[user_id])
                hours = remaining.seconds // 3600
                minutes = (remaining.seconds % 3600) // 60

                await update.message.reply_text(
                    f"Вы уже отправляли обращение.\n"
                    f"Попробуйте снова через {hours} ч {minutes} мин."
                )
                return

    # ================== ПЕРЕСЫЛКА ==================
    try:
        await context.bot.forward_message(
            chat_id=ADMIN_CHAT_ID,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )
    except Exception as e:
        logging.error(f"Ошибка пересылки: {e}")
        await update.message.reply_text(
            "Произошла ошибка при отправке сообщения 😔\n"
            "Попробуйте позже."
        )
        return

    # Запоминаем время (даже для админа — не мешает)
    last_request_time[user_id] = now

    # ================== ОТВЕТ ПОЛЬЗОВАТЕЛЮ ==================
    await update.message.reply_text(
        "Спасибо за обращение 🙌\n"
        "Мы получили ваше сообщение и постараемся ответить в ближайшее время."
    )

# ================== ЗАПУСК ==================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    print("✅ Бот запущен")
    app.run_polling()


if __name__ == "__main__":
    main()

