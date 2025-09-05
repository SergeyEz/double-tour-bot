from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# === НАСТРОЙКИ ===
TOKEN = "8321023518:AAETz3u5vnF68mcB6Bm5AYCj-W4CuX4qp9c"  # ← ЗАМЕНИТЬ!

# Ссылки
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
    "sheregesh_schedule": None,  # пока нет
}

# === ОБРАБОТЧИКИ ===

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
        # Если вызван через /start — отправляем новое сообщение
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        # Если вызван через кнопку — редактируем текущее сообщение
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def mountain_tours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("📍 Кировск", callback_data="kirovsk")],
        [InlineKeyboardButton("📍 Шерегеш", callback_data="sheregesh")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "🌍 Выбери направление:",
        reply_markup=reply_markup
    )


async def kirovsk_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("ℹ️ Инфо о туре", url=LINKS["kirovsk_info"])],
        [InlineKeyboardButton("📅 Расписание/цены", url=LINKS["kirovsk_schedule"])],
        [InlineKeyboardButton("✅ Бронь", url=LINKS["booking"])],
        [InlineKeyboardButton("❓ Остались вопросы", url=LINKS["booking"])],
        [InlineKeyboardButton("🔄 Начать заново", callback_data="start")]
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
        [InlineKeyboardButton("📅 Расписание/цены", url=LINKS["sheregesh_schedule"] or "https://vk.com/double.community")],  # если пусто — подставим ВК
        [InlineKeyboardButton("✅ Бронь", url=LINKS["booking"])],
        [InlineKeyboardButton("❓ Остались вопросы", url=LINKS["booking"])],
        [InlineKeyboardButton("🔄 Начать заново", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "🔥 *Тур в Шерегеш*\n\n"
        "Самый крутой сноубордический курорт Сибири!",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


# === ОБРАБОТЧИК КНОПОК ===
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


# === ЗАПУСК БОТА ===
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Бот запущен! Ожидание команд...")
    app.run_polling()

if __name__ == "__main__":
    main()