import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Состояния бота
SELECT_LANGUAGE, ENTER_ROOM = range(2)


# Клавиатура выбора языка
def get_language_keyboard():
    keyboard = [
        [KeyboardButton("🇷🇺 Русский"), KeyboardButton("🇬🇧 English")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


# Клавиатура главного меню
def get_main_keyboard(language):
    if language == "russian":
        keyboard = [
            [KeyboardButton("🔍 Найти кабинет")],
            [KeyboardButton("🔄 Сменить язык"), KeyboardButton("❓ Помощь")]
        ]
    else:  # english
        keyboard = [
            [KeyboardButton("🔍 Find room")],
            [KeyboardButton("🔄 Change language"), KeyboardButton("❓ Help")]
        ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# Тексты на разных языках
TEXTS = {
    "russian": {
        "welcome": "🏛️ Добро пожаловать в навигатор по корпусу!",
        "choose_action": "Пожалуйста, выберите действие:",
        "room_prompt": "Введите номер кабинета (например: 101, 205, 301):",
        "search_again": "🔍 Найти другой кабинет",
        "back_to_menu": "⬅️ В главное меню",
        "help_text": """🤖 *Помощь по боту*

Введите номер кабинета который хотите найти.

*Примеры:*
• 101
• 205  
• 301

Бот покажет расположение и информацию о кабинете.""",
        "no_database": "❌ *База данных кабинетов временно недоступна*\n\nВ настоящее время мы обновляем информацию о расположении кабинетов. Пожалуйста, обратитесь к администрации корпуса для уточнения информации.",
        "invalid_room": "❌ Пожалуйста, введите корректный номер кабинета (только цифры)"
    },
    "english": {
        "welcome": "🏛️ Welcome to the building navigator!",
        "choose_action": "Please select an action:",
        "room_prompt": "Enter the room number (e.g.: 101, 205, 301):",
        "search_again": "🔍 Find another room",
        "back_to_menu": "⬅️ Back to main menu",
        "help_text": """🤖 *Bot Help*

Enter the room number you want to find.

*Examples:*
• 101
• 205
• 301

The bot will show the location and information about the room.""",
        "no_database": "❌ *Room database temporarily unavailable*\n\nWe are currently updating room location information. Please contact the building administration for details.",
        "invalid_room": "❌ Please enter a valid room number (digits only)"
    }
}


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏛️ Welcome! Добро пожаловать!\n\n"
        "Please choose your language / Пожалуйста, выберите язык:",
        reply_markup=get_language_keyboard()
    )
    return SELECT_LANGUAGE

# Обработка выбора языка
async def select_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_choice = update.message.text

    if user_choice == "🇷🇺 Русский":
        context.user_data['language'] = "russian"
    elif user_choice == "🇬🇧 English":
        context.user_data['language'] = "english"
    else:
        await update.message.reply_text(
            "Please choose a language from the buttons / Пожалуйста, выберите язык из кнопок")
        return SELECT_LANGUAGE

    language = context.user_data['language']
    texts = TEXTS[language]

    await update.message.reply_text(
        f"{texts['welcome']}\n\n{texts['choose_action']}",
        reply_markup=get_main_keyboard(language)
    )
    return ENTER_ROOM


# Главное меню
async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = context.user_data.get('language', 'russian')
    texts = TEXTS[language]
    user_text = update.message.text

    if "🔍" in user_text or "find" in user_text or "Найти" in user_text:
        await update.message.reply_text(texts['room_prompt'])
        return ENTER_ROOM
    elif "🔄" in user_text or "change" in user_text or "Сменить" in user_text:
        await update.message.reply_text(
            "Choose language / Выберите язык:",
            reply_markup=get_language_keyboard()
        )
        return SELECT_LANGUAGE
    elif "❓" in user_text or "help" in user_text or "Помощь" in user_text:
        await update.message.reply_text(texts['help_text'], parse_mode='Markdown')
        return ENTER_ROOM

    await update.message.reply_text(texts['room_prompt'])
    return ENTER_ROOM


# Поиск кабинета
async def search_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = context.user_data.get('language', 'russian')
    texts = TEXTS[language]
    room_number = update.message.text.strip()

    # Проверяем, что введены только цифры
    if not room_number.isdigit():
        await update.message.reply_text(texts['invalid_room'])
        return ENTER_ROOM

    # Заглушка - база данных недоступна
    response = f"""
🔍 *Поиск кабинета {room_number}*

{texts['no_database']}"""

    # Клавиатура для дальнейших действий
    keyboard = [
        [KeyboardButton(texts['search_again']), KeyboardButton(texts['back_to_menu'])]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(response, parse_mode='Markdown', reply_markup=reply_markup)
    return ENTER_ROOM


# Обработка возврата в меню
async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = context.user_data.get('language', 'russian')
    texts = TEXTS[language]

    await update.message.reply_text(
        texts['welcome'],
        reply_markup=get_main_keyboard(language)
    )
    return ENTER_ROOM


# Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "До свидания! / Goodbye!",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("/start")]], resize_keyboard=True)
    )
    return ConversationHandler.END


# Основная функция
def main():
    TOKEN = "8318744555:AAGh9Z-LG6Eym1_xFeewS_j8ZvfmbbBYrR4"

    application = Application.builder().token(TOKEN).build()

    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECT_LANGUAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, select_language),
                CommandHandler('start', start)
            ],
            ENTER_ROOM: [
                MessageHandler(filters.Regex(r'^(🔍|🔄|❓|Найти|Find|Сменить|Change|Помощь|Help)'), handle_main_menu),
                MessageHandler(filters.Regex(r'^(⬅️|Back|В главное)'), back_to_menu),
                MessageHandler(filters.TEXT & ~filters.COMMAND, search_room),
                CommandHandler('menu', back_to_menu)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)

    print("Бот запущен...")
    application.run_polling()


if __name__ == '__main__':
    main()