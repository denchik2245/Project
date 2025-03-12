import yaml
import logging
import logging.config
from bot.telegram_bot import start_bot

def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)

def init_logging(config_path: str):
    logging.config.fileConfig(config_path, disable_existing_loggers=False)

def main():
    # Загрузка конфигурации
    config = load_config("config/config.yaml")
    # Инициализация логирования
    init_logging("config/logging.conf")
    logging.info("Запуск Telegram-бота")
    # Запуск бота
    start_bot(config)

if __name__ == '__main__':
    main()
