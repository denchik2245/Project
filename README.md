## **config/**
_config.yaml_ - Здесь хранятся все настройки проекта: токены для Telegram-бота, API-ключи, URL-адреса целевых сервисов и прочие конфигурационные параметры

_logging.conf_ - Файл конфигурации для модуля логирования (например, на базе стандартного модуля logging). Здесь задаются уровни логов, формат вывода, ротация логов и т.д. Это помогает отслеживать работу приложения и оперативно выявлять ошибки

## **data/**
Директория для хранения временных данных, кэшей, локальных баз данных (например, SQLite) или файлов с результатами парсинга. Такой подход помогает избежать повторных запросов к удалённым сайтам и улучшает производительность

## **parsers/**
_init.py_ - Позволяет трактовать эту папку как пакет. Может содержать общие настройки для всех парсеров

## **bot/**
Модуль, отвечающий за взаимодействие с пользователями через Telegram

_telegram_bot.py_ - Основной файл с логикой Telegram-бота: настройка обработчиков команд, запуск polling/webhook, обработка сообщений от пользователей (например, ввод городов, выбор маршрута и т.п.). Здесь подключается основной цикл обработки событий

_callbacks.py_ - Файл для обработки inline-кнопок и callback-запросов. При наличии интерактивных элементов в интерфейсе бота это позволит разделить код для удобства поддержки

## **neural/**
Модуль для работы с локальной нейросетью через Ollama

_ollama_integration.py_ - Файл для интеграции с локальной нейросетью. Здесь реализуются функции отправки запросов к нейросети, обработки полученных ответов, возможно, формирования подсказок или дополнительных рекомендаций для пользователя

## **utils/**
Общие утилиты и вспомогательные функции, используемые в разных частях проекта

_http_client.py_ - Универсальный HTTP-клиент для отправки запросов с обработкой ошибок, повторными попытками, таймаутами и прокси (если требуется). Он будет использоваться в модулях парсинга

_parser_utils.py_ - Общие функции для работы с данными: парсинг HTML, обработка DOM, регулярные выражения для извлечения нужных данных

_db_utils.py_ - Здесь будут функции для работы с базой данных: создание таблиц, чтение и запись данных

_exceptions.py_ - Определение пользовательских исключений, что позволяет централизованно обрабатывать ошибки, возникающие при парсинге, работе с HTTP или взаимодействии с Telegram

## **main.py**
Главная точка входа в приложение. Здесь происходит:
- Загрузка конфигурации из config.yaml.
- Инициализация логирования.
- Запуск Telegram-бота (инициализация модуля bot).
- Возможно, настройка периодических задач (например, обновление кэша или парсинг данных в фоновом режиме).

## **requirements.txt**
Файл, содержащий список необходимых зависимостей (библиотеки для работы с Telegram API, requests/selenium/BeautifulSoup для парсинга, библиотеки для работы с нейросетью, и прочее). Это упрощает развёртывание проекта на новом сервере или машине разработчика