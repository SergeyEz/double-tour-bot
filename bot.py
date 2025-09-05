# bot.py
import os
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import json
import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# === Настройка логирования ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === Токен бота из переменной окружения ===
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Не задана переменная окружения BOT_TOKEN")

# === Ссылки ===
LINKS = {
    "site": "https://doubleride.ru",
    "inst": "https://www.instagram.com/double.community?igsh=dTY3bDU0ZWprdmg0",
    "vk": "https://vk.com/double.community",
    "tg_channel": "https://t.me/Doubleride",
    "corob": "https://vk.com/board88867",  # Запись на выезд коробом
    "booking": "https://vk.com/im?sel=-88867",  # Бронь и вопросы
    "kirovsk_info": "https://vk.com/@-88867-pro-tur-v-hibiny",
    "kirovsk_schedule": "https://vk.com/@-88867-raspisanie-gornolyzhnyh-turov-na-sezon-2021-22-vmeste-s-doub",
    "sheregesh_info": "https://vk.com/@-88867-gornolyzhnyi-tur-v-sheregesh-daty-ceny-programma-faq",
    "sheregesh_schedule": "https://vk.com/double.community",  # резерв
}

# === Обработчики команд ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌐 Сайт", url=LINKS["site"])],
        [InlineKeyboardButton("📸 Instagram", url=LINKS["inst"])],
        [InlineKeyboardButton("💬 ВКонтакте", url=LINKS["vk"])],
        [InlineKeyboardButton("📢 Телеграм-канал", url=LINKS["tg_channel"])],
        [InlineKeyboardButton("🏂 Запись на выезд в Короб", url=LINKS["corob"])],
        [InlineKeyboardButton("🏔 Туры в горы", callback_data="mountain_tours")],
        [InlineKeyboardButton("🔄 Начать заново", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "👋 Привет! Это официальный бот *DOUBLE*!\n\n"
        "Выбери, куда хочешь попасть:"
    )

    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "ℹ️ *Справка по боту*\n\n"
        "Доступные команды:\n"
        "/start — главное меню\n"
        "/help — эта справка\n\n"
        "Если остались вопросы — нажми кнопку *«Остались вопросы»*."
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def mountain_tours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("📍 Кировск", callback_data="kirovsk")],
        [InlineKeyboardButton("📍 Шерегеш", callback_data="sheregesh")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("🌍 Выбери направление:", reply_markup=reply_markup)


async def kirovsk_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("ℹ️ Инфо о туре", url=LINKS["kirovsk_info"])],
        [InlineKeyboardButton("📅 Расписание/цены", url=LINKS["kirovsk_schedule"])],
        [InlineKeyboardButton("✅ Бронь", url=LINKS["booking"])],
        [InlineKeyboardButton("❓ Остались вопросы", url=LINKS["booking"])],
        [InlineKeyboardButton("⬅️ Назад", callback_data="mountain_tours")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "📍 *Тур в Кировск*\n\n"
        "Горнолыжный курорт Хибины, северное сияние, экстрим и природа!",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def sheregesh_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("ℹ️ Инфо о туре", url=LINKS["sheregesh_info"])],
        [InlineKeyboardButton("📅 Расписание/цены", url=LINKS["sheregesh_schedule"])],
        [InlineKeyboardButton("✅ Бронь", url=LINKS["booking"])],
        [InlineKeyboardButton("❓ Остались вопросы", url=LINKS["booking"])],
        [InlineKeyboardButton("⬅️ Назад", callback_data="mountain_tours")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "🔥 *Тур в Шерегеш*\n\n"
        "Самый крутой сноубордический курорт Сибири!",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


# === Обработчик кнопок ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == "mountain_tours":
        await mountain_tours(update, context)
    elif data == "kirovsk":
        await kirovsk_menu(update, context)
    elif data == "sheregesh":
        await sheregesh_menu(update, context)
    elif data == "start":
        await start(update, context)


# === HTTP-сервер для вебхука ===
class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == f"/{TOKEN}":
            try:
                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length)
                data = json.loads(body.decode('utf-8'))
                update = Update.de_json(data, application.bot)

                asyncio.run_coroutine_threadsafe(
                    application.update_queue.put(update),
                    loop
                )

                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")
            except Exception as e:
                logger.error(f"Ошибка вебхука: {e}")
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Telegram Bot is running!")
        else:
            self.send_response(404)
            self.end_headers()


# === Запуск бота и сервера ===
def run():
    global application, loop
    application = Application.builder().token(TOKEN).build()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler))

    # Запускаем бота в фоне
    loop.create_task(application.run_polling())

    # Запускаем веб-сервер
    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(('', port), WebhookHandler)
    logger.info(f"🚀 Веб-сервер запущен на порту {port}")
    server.serve_forever()


if __name__ == "__main__":
    run()