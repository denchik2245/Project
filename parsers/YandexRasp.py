import os
import sys
import yaml
import requests
import json
from datetime import datetime


def load_config(config_file):
    """
    Загружает конфигурацию из YAML-файла.
    """
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Файл конфигурации {config_file} не найден.")
        sys.exit(1)
    except yaml.YAMLError as exc:
        print("Ошибка при разборе YAML файла:", exc)
        sys.exit(1)


def fetch_schedule(api_key, from_station, to_station, date, lang='ru_RU', transport_types='train'):
    """
    Выполняет запрос к API Яндекс Расписания по эндпоинту /search/ с фильтром по типу транспорта.
    """
    endpoint = "https://api.rasp.yandex.net/v3.0/search/"
    params = {
        "apikey": api_key,
        "format": "json",
        "from": from_station,
        "to": to_station,
        "date": date,
        "lang": lang,
        "page": 1,
        "transport_types": transport_types
    }
    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print("Ошибка при выполнении запроса к API:", e)
        sys.exit(1)


def format_datetime(iso_str):
    """
    Преобразует строку ISO-формата в формат "ДД.MM.ГГГГ ЧЧ:ММ".
    """
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return iso_str


def format_duration(duration_seconds):
    """
    Преобразует длительность в секундах в строку вида "X ч Y мин".
    """
    total_minutes = int(duration_seconds // 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours} ч {minutes} мин"


def fetch_thread_details(thread_link, api_key):
    """
    Делает запрос к API для получения дополнительных деталей по ссылке thread_method_link.
    Если в ссылке не указан протокол и параметры, они добавляются.
    """
    if not thread_link.startswith("http"):
        thread_link = "https://" + thread_link
    # Добавляем параметры apikey и формат в URL
    if "?" in thread_link:
        thread_link += f"&apikey={api_key}&format=json"
    else:
        thread_link += f"?apikey={api_key}&format=json"
    try:
        response = requests.get(thread_link)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print("Ошибка при получении деталей рейса:", e)
        return None


def print_details(details, indent=2):
    """
    Рекурсивно выводит словари и списки с отступами для удобного чтения.
    """
    indent_str = " " * indent
    if isinstance(details, dict):
        for key, value in details.items():
            if isinstance(value, (dict, list)):
                print(f"{indent_str}{key}:")
                print_details(value, indent + 2)
            else:
                print(f"{indent_str}{key}: {value}")
    elif isinstance(details, list):
        for idx, item in enumerate(details, start=1):
            print(f"{indent_str}[{idx}]:")
            print_details(item, indent + 2)
    else:
        print(f"{indent_str}{details}")


def print_pretty_schedule(schedule, api_key):
    """
    Выводит всю доступную информацию из ответа API Яндекс Расписания в красиво отформатированном виде,
    включая детали рейса, полученные по ссылке thread_method_link.
    """
    # Блок 1. Информация о поиске
    search = schedule.get("search", {})
    print("=" * 80)
    print("Информация о поиске:")
    print("=" * 80)
    print(f"Дата: {search.get('date', 'N/A')}")
    from_info = search.get("from", {})
    to_info = search.get("to", {})
    print(f"Откуда: {from_info.get('title', 'N/A')} (код: {from_info.get('code', 'N/A')})")
    print(f"Куда:   {to_info.get('title', 'N/A')} (код: {to_info.get('code', 'N/A')})")
    print()

    # Блок 2. Пагинация
    pagination = schedule.get("pagination")
    if pagination:
        print("=" * 80)
        print("Информация о пагинации:")
        print("=" * 80)
        for key, value in pagination.items():
            print(f"{key.capitalize()}: {value}")
        print()

    # Блок 3. Сегменты (рейсы)
    segments = schedule.get("segments", [])
    if segments:
        print("=" * 80)
        print("Найденные сегменты (рейсы):")
        print("=" * 80)
        for idx, seg in enumerate(segments, start=1):
            thread = seg.get("thread", {})
            dep_iso = seg.get("departure", "")
            arr_iso = seg.get("arrival", "")
            dep_time = format_datetime(dep_iso)
            arr_time = format_datetime(arr_iso)
            duration = seg.get("duration", 0)
            formatted_duration = format_duration(duration)
            dep_station = seg.get("from", {}).get("title", "N/A")
            arr_station = seg.get("to", {}).get("title", "N/A")
            train_number = thread.get("number", "N/A")
            train_title = thread.get("title", "N/A")
            carrier = thread.get("carrier", {}).get("title", "N/A")
            vehicle = thread.get("vehicle", "N/A")
            dep_terminal = seg.get("departure_terminal", "")
            arr_terminal = seg.get("arrival_terminal", "")

            print("-" * 80)
            print(f"Сегмент #{idx}: {train_number} - {train_title}")
            print(f"Перевозчик: {carrier}")
            print(f"Тип транспорта: {vehicle}")
            print(f"Отправление: {dep_time} из {dep_station}" +
                  (f" (Терминал: {dep_terminal})" if dep_terminal else ""))
            print(f"Прибытие:   {arr_time} в {arr_station}" +
                  (f" (Терминал: {arr_terminal})" if arr_terminal else ""))
            print(f"Длительность: {formatted_duration}")

            # Вывод информации о цене (tickets_info)
            tickets_info = seg.get("tickets_info", {})
            places = tickets_info.get("places", [])
            if places:
                print("Цены:")
                for price_info in places:
                    price_obj = price_info.get("price", {})
                    if isinstance(price_obj, dict) and "whole" in price_obj:
                        whole = price_obj.get("whole", "N/A")
                        cents = price_obj.get("cents", 0)
                        if cents:
                            price_str = f"{whole}.{cents:02d}"
                        else:
                            price_str = f"{whole}"
                    else:
                        price_str = str(price_info.get("price", "N/A"))
                    currency = price_info.get("currency", "")
                    fare_class = price_info.get("name", "N/A")
                    print(f"  {fare_class}: {price_str} {currency}")

            # Дополнительные детали рейса (вместо ссылки)
            thread_link = thread.get("thread_method_link", "")
            if thread_link:
                details = fetch_thread_details(thread_link, api_key)
                if details:
                    print("Детали рейса:")
                    print_details(details, indent=4)
            else:
                print("Доп. информация: N/A")
            print("-" * 80)
            print()
    else:
        print("Сегменты не найдены.")
        print()

    # Блок 4. Интервальные сегменты (если есть)
    interval_segments = schedule.get("interval_segments", [])
    if interval_segments:
        print("=" * 80)
        print("Интервальные сегменты:")
        print("=" * 80)
        for idx, seg in enumerate(interval_segments, start=1):
            print(f"Интервальный сегмент #{idx}:")
            print(f"От: {seg.get('from', {}).get('title', 'N/A')} (код: {seg.get('from', {}).get('code', 'N/A')})")
            print(f"До: {seg.get('to', {}).get('title', 'N/A')} (код: {seg.get('to', {}).get('code', 'N/A')})")
            thread = seg.get("thread", {})
            print(f"Рейс: {thread.get('number', 'N/A')} - {thread.get('title', 'N/A')}")
            interval = thread.get("interval", {})
            print(f"Интервал работы: с {interval.get('begin_time', 'N/A')} по {interval.get('end_time', 'N/A')}")
            print("-" * 80)
        print()


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(script_dir, "..", "config", "config.yaml")

    config = load_config(config_file)
    api_key = config.get("parsing", {}).get("YandexRasp")
    if not api_key:
        print("API-ключ для YandexRasp не найден в файле конфигурации.")
        sys.exit(1)

    # Для поездов рекомендуется использовать коды городов:
    # Симферополь - "c146", Москва - "c213"
    from_station = "c56"  # Челябинск
    to_station = "c54"  # Москва
    date = "2025-03-17"  # Дата отправления

    schedule = fetch_schedule(api_key, from_station, to_station, date, transport_types="bus")
    print_pretty_schedule(schedule, api_key)


if __name__ == "__main__":
    main()
