import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackContext,
    ContextTypes,
    filters
)

logger = logging.getLogger(__name__)

# ШАГИ (состояния) нашего "сценария" общения
STEP_DESTINATION, STEP_ACCOMMODATION, STEP_FOOD, STEP_PLACES, STEP_SUMMARY = range(5)


# ---- Этап 1. Пользователь вводит общую информацию о поездке ----
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Начало сценария: просим ввести исходные данные.
    """
    await update.message.reply_text(
        "Привет! Начнем составление вашего путешествия.\n"
        "Введите следующую информацию через запятую:\n\n"
        "Ваш город, Город который хотите посетить, Даты приезда и отъезда, Количество взрослых гостей\n\n"
        "Например:\n"
        "Москва, Санкт-Петербург, 2025-07-01 - 2025-07-05, 2\n\n"
        "Пришлите эти данные одним сообщением."
    )
    return STEP_DESTINATION


async def get_travel_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработка ввода пользователя по поводу транспорт/билеты.
    """
    user_input = update.message.text
    logger.info(f"Пользователь ввёл данные о поездке: {user_input}")

    # Здесь можно сохранить данные о поездке в context.user_data, чтобы использовать далее
    context.user_data["travel_info"] = user_input

    # "Ищем оптимальный транспорт и билеты..."
    await update.message.reply_text(
        "Ищем оптимальный транспорт и билеты...\n"
        "(тут будет парсинг Aviasales, Яндекс расписаний и т.д.)"
    )
    # Заглушка: имитация поиска
    # Здесь будет реальный код парсинга, например:
    # flights = parse_aviasales(...), parse_yandex_schedules(...)
    # context.user_data["flights"] = ... (сохраняем результаты)

    # После парсинга выводим следующее сообщение:
    await update.message.reply_text(
        "Транспорт и билеты найдены!\n\n"
        "Теперь перейдем к поиску жилья. Введите следующую информацию через запятую:\n"
        "(прямо сейчас точных данных нет, это зависит от API)\n\n"
        "Например:\n"
        "Предпочитаемые даты и бюджет, Удобное расположение и т.д.\n\n"
        "Пришлите эти данные одним сообщением."
    )
    return STEP_ACCOMMODATION


# ---- Этап 2. Пользователь вводит данные для поиска жилья ----
async def get_accommodation_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    logger.info(f"Пользователь ввёл данные о жилье: {user_input}")

    context.user_data["accommodation_info"] = user_input

    # "Ищем оптимальные варианты жилья..."
    await update.message.reply_text(
        "Ищем оптимальные варианты жилья...\n"
        "(тут будет парсинг Booking, Суточно.ру и т.д.)"
    )
    # Заглушка: имитация поиска жилья
    # context.user_data["accommodations"] = ...

    await update.message.reply_text(
        "Жилье найдено!\n\n"
        "Теперь перейдём к поиску столовых, кафе и ресторанов поблизости.\n"
        "Сейчас мы будем искать варианты еды рядом с предложенным жильем.\n"
        "Нажмите что-нибудь или просто напишите 'далее' для запуска."
    )
    return STEP_FOOD


# ---- Этап 3. Поиск столовых, кафе, ресторанов ----
async def get_food_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    logger.info(f"Пользователь ввёл данные для поиска еды: {user_input}")

    # "Ищем лучшие столовые, кафе и рестораны..."
    await update.message.reply_text(
        "Ищем лучшие столовые, кафе и рестораны...\n"
        "(тут будет парсинг Яндекс.Карт, 2GIS и т.д.)"
    )
    # Заглушка: имитация парсинга
    # context.user_data["food_options"] = ...

    await update.message.reply_text(
        "Столовые, кафе и рестораны найдены!\n\n"
        "Теперь перейдем к следующему шагу: Куда сходить и где прогуляться.\n"
        "Выберите, что вас интересует:\n"
        "– Музеи,\n"
        "– Искусство и театр,\n"
        "– На открытом воздухе,\n"
        "... и т.д.\n\n"
        "Введите подходящие варианты через запятую одним сообщением."
    )
    return STEP_PLACES


# ---- Этап 4. Поиск достопримечательностей, мест для досуга ----
async def get_places_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    logger.info(f"Пользователь ввёл интересующие категории: {user_input}")

    # "Ищем лучшие места по выбранным категориям..."
    await update.message.reply_text(
        "Ищем лучшие места по вашим интересам...\n"
        "(тут будет парсинг Tripadvisor и т.д.)"
    )
    # Заглушка: имитация
    # context.user_data["places"] = ...

    # Предлагаем кнопку (или пользователь просто вводит команду) для получения сводки:
    button = InlineKeyboardButton("Получить сводку", callback_data="summary")
    keyboard = InlineKeyboardMarkup([[button]])
    await update.message.reply_text(
        text="Все данные найдены, нажмите кнопку, чтобы получить итоговую сводку:",
        reply_markup=keyboard
    )

    # Переходим в финальное состояние, но ждём нажатия на кнопку
    return STEP_SUMMARY


# ---- Этап 5. Итоговая сводка ----
async def send_summary_callback(update: Update, context: CallbackContext) -> None:
    """
    При нажатии на кнопку "Получить сводку" выдаём результат.
    """
    query = update.callback_query
    await query.answer()  # подтверждение callback

    # Здесь уже генерируем сводку по всем собранным данным.
    # В более сложном варианте — обращение к локальной нейросети для выбора лучших вариантов.
    travel_info = context.user_data.get("travel_info", "Неизвестно")
    accommodations_info = context.user_data.get("accommodation_info", "Неизвестно")

    # Пример сводки (заглушка)
    summary = (
        "Итоговая сводка по вашему путешествию:\n\n"
        f"Данные о поездке: {travel_info}\n"
        f"Данные о жилье: {accommodations_info}\n\n"
        "Оптимальный транспорт: (здесь будут выводиться реальные данные)\n"
        "Оптимальное жильё: (здесь будут выводиться реальные данные)\n"
        "Столовые/кафе: (список)\n"
        "Достопримечательности: (список)\n\n"
        "Спасибо, что воспользовались нашим ботом!"
    )

    await query.edit_message_text(text=summary)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Пример fallback: досрочное завершение.
    """
    await update.message.reply_text("Вы прервали процесс. Если хотите начать заново, введите /start.")
    return ConversationHandler.END


def start_bot(config: dict):
    token = config['telegram']['token']

    # Создаём приложение
    app = ApplicationBuilder().token(token).build()

    # ConversationHandler управляет логикой шагов
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            STEP_DESTINATION: [MessageHandler(filters.TEXT, get_travel_info)],
            STEP_ACCOMMODATION: [MessageHandler(filters.TEXT, get_accommodation_info)],
            STEP_FOOD: [MessageHandler(filters.TEXT, get_food_info)],
            STEP_PLACES: [MessageHandler(filters.TEXT, get_places_info)],
            STEP_SUMMARY: []  # Когда мы показываем кнопку, ждём callback, а не текст
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )

    # Обработчик нажатия кнопки "Получить сводку"
    app.add_handler(conv_handler)
    app.add_handler(
        # Обработка callback_data="summary"
        MessageHandler(filters.COMMAND, lambda u, c: None)  # пустая заглушка, чтобы не было конфликтов
    )
    app.add_handler(
        # Ловим callback с данным "summary"
        CommandHandler("summary", lambda u, c: None)  # Заглушка – если кто-то решит ввести /summary
    )
    # Проще всего добавить отдельный CallbackQueryHandler:
    from telegram.ext import CallbackQueryHandler
    app.add_handler(CallbackQueryHandler(send_summary_callback, pattern="^summary$"))

    # Запуск polling
    logger.info("Бот запущен. Ожидание сообщений...")
    app.run_polling()
