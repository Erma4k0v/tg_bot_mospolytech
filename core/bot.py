import logging
from database.db import get_room_info
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import re


# Функция нормализации букв
def normalize_room_number(room_number):
    """Приводит русские буквы к английским (только a, b, v)"""
    russian_to_english = {
        'а': 'a',  # русская 'а' → английская 'a'
        'в': 'v',  # русская 'в' → английская 'v'
        'б': 'b',  # русская 'б' → английская 'b'
    }

    normalized = ''
    for char in room_number:
        lower_char = char.lower()
        if lower_char in russian_to_english:
            if char.isupper():
                normalized += russian_to_english[lower_char].upper()
            else:
                normalized += russian_to_english[lower_char]
        else:
            normalized += char

    return normalized


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
        "choose_action": """Привет! 👋 Я — ваш путеводитель по корпусу Московского Политеха по адресу ул. Павла Корчагина, 22 🏢. Готов помочь найти нужную аудиторию! 🔍🎓

🔢 Чтобы найти аудиторию:
Введите номер аудитории (например, 305). Я покажу вам, на каком этаже она находится и как добраться до нее.

📝 Обратите внимание:
Корпус 5-этажный 🏢
Нумерация аудиторий —410, 415, 407 и так далее
Этажи с 1 по 5 📝""",
        "room_prompt": "Введите номер кабинета (например: 101, 205, 301):",
        "search_again": "🔍 Найти другой кабинет",
        "back_to_menu": "⬅️ В главное меню",
        "help_text": """🤖 *Помощь по боту*

Введите номер кабинета который хотите найти.

*Примеры:*
• 101
• 205  
• 301
• 333a
• 205b
• 410в

Бот покажет расположение и информацию о кабинете.""",
        "no_database": "❌ *База данных кабинетов временно недоступна*\n\nВ настоящее время мы обновляем информацию о расположении кабинетов. Пожалуйста, обратитесь к администрации корпуса для уточнения информации.",
        "invalid_room": "❌ Пожалуйста, введите корректный номер кабинета (цифры + опционально буква a/b/v)"
    },
    "english": {
        "choose_action": """Hello! 👋 I'm your guide to the Moscow Polytech building at 22 Pavel Korchagin Street 🏢. I'm ready to help you find the right classroom! 🔍🎓

🔢 To find a classroom:
Enter the room number (for example, 305). I'll show you which floor it's on and how to get there.

📝 Please note:
The building has 5 floors 🏢
The classroom numbering is like 410, 415, 407, and so on.
Floors are from 1 to 5 📝""",
        "room_prompt": "Enter the room number (e.g.: 101, 205, 301, 333a):",
        "search_again": "🔍 Find another room",
        "back_to_menu": "⬅️ Back to main menu",
        "help_text": """🤖 *Bot Help*

Enter the room number you want to find.

*Examples:*
• 101
• 205
• 301
• 333a
• 205b

The bot will show the location and information about the room.""",
        "no_database": "❌ *Room database temporarily unavailable*\n\nWe are currently updating room location information. Please contact the building administration for details.",
        "invalid_room": "❌ Please enter a valid room number (digits + optional letter a/b/v)"
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
        texts['choose_action'],
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

    # Нормализуем буквы (русские → английские)
    normalized_number = normalize_room_number(room_number)

    # Проверяем формат: цифры + опционально буквы a,b,v (русские или английские)
    if not re.match(r'^\d+[abvABVаАбБвВ]?$', room_number):
        await update.message.reply_text(texts['invalid_room'])
        return ENTER_ROOM

    # Ищем кабинет в БД (используем нормализованный номер)
    room_info = get_room_info(normalized_number.upper())  # Приводим к верхнему регистру

    if not room_info:
        response = f"""
🔍 *Поиск кабинета {room_number}*

❌ Кабинет {room_number} не найден в базе данных.
Проверьте правильность номера."""

        # Клавиатура для дальнейших действий
        keyboard = [
            [KeyboardButton(texts['search_again']), KeyboardButton(texts['back_to_menu'])]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(response, parse_mode='Markdown', reply_markup=reply_markup)
        return ENTER_ROOM

    # Отправляем фото с разными подписями
    photo_urls = room_info['photo_urls']
    if photo_urls:
        for i, photo_url in enumerate(photo_urls, 1):
            if i == 1:  # Первая фотка
                caption = "📍 *Иди прямо*"
            elif i == len(photo_urls):  # Последняя фотка
                caption = "✅ *Ты на месте!*"
            else:  # Средние фотки
                caption = "📍 *Продолжай идти прямо*"

            try:
                await update.message.reply_photo(
                    photo_url,
                    caption=caption,
                    parse_mode='Markdown'
                )
            except Exception as e:
                await update.message.reply_text(f"❌ Ошибка загрузки фото {i}")

    # Основное сообщение после фото
    response = f"""
🏢 *Кабинет {room_info['number']}*

📋 *Этаж:* {room_info['floor']}
📝 *Описание:* {room_info['description']}"""

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
        texts['choose_action'],
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