import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
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
    "corob": "https://vk.com/board88867",
    "booking": "https://vk.com/im?sel=-88867",
    "kirovsk_info": "https://vk.com/@-88867-pro-tur-v-hibiny",
    "kirovsk_schedule": "https://vk.com/@-88867-raspisanie-gornolyzhnyh-turov-na-sezon-2021-22-vmeste-s-doub",
    "sheregesh_info": "https://vk.com/@-88867-gornolyzhnyi-tur-v-sheregesh-daty-ceny-programma-faq",
    "sheregesh_schedule": "https://vk.com/double.community",
}

# === Простой HTTP сервер для Render ===
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot is running!')
    
    def log_message(self, format, *args):
        logger.info("%s - %s" % (self.address_string(), format % args))

def run_http_server():
    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    logger.info(f"HTTP server running on port {port}")
    server.serve_forever()

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
        try:
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        except Exception as e:
            if "Message is not modified" not in str(e):
                logger.error(f"Ошибка в start: {e}")

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

    try:
        await query.edit_message_text("🌍 Выбери направление:", reply_markup=reply_markup)
    except Exception as e:
        if "Message is not modified" not in str(e):
            logger.error(f"Ошибка в mountain_tours: {e}")

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

    try:
        await query.edit_message_text(
            "📍 *Тур в Кировск*\n\n"
            "Горнолыжный курорт Хибины, северное сияние, экстрим и природа!",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        if "Message is not modified" not in str(e):
            logger.error(f"Ошибка в kirovsk_menu: {e}")

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

    try:
        await query.edit_message_text(
            "🔥 *Тур в Шерегеш*\n\n"
            "Самый крутой сноубордический курорт Сибии!",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        if "Message is not modified" not in str(e):
            logger.error(f"Ошибка в sheregesh_menu: {e}")

# === Обработчик кнопок ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data

    if data == "mountain_tours":
        await mountain_tours(update, context)
    elif data == "kirovsk":
        await kirovsk_menu(update, context)
    elif data == "sheregesh":
        await sheregesh_menu(update, context)
    elif data == "start":
        await start(update, context)

# === Главная функция запуска ===
def main():
    # Запускаем HTTP сервер в отдельном потоке
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()

    # Создаём приложение бота
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler))

    # Запускаем polling бота
    print("Бот запускается...")
    logger.info("Бот запущен и готов к работе!")
    application.run_polling()

if __name__ == "__main__":
    main()