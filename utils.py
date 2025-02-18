from datetime import datetime
import logging

from constants import (
    REQUIRED_KEYS,
    RESPONSE_KEYS,
    HOMEWORK_TYPES,
    HOMEWORK_VERDICTS,
    DATE_FORMAT,
)


class TelegramErrorHandler(logging.Handler):
    """Обработчик логов, отправляющий ошибки в Telegram."""

    def __init__(self, bot, chat_id):
        """Инициализация обработчика логов для отправки ошибок в Telegram."""
        super().__init__(level=logging.ERROR)
        self.bot = bot
        self.chat_id = chat_id
        self.last_error_message = None

    def emit(self, record):
        """Отправляет сообщение в Telegram только при новой ошибке."""
        log_entry = self.format(record)
        if log_entry != self.last_error_message:
            self.last_error_message = log_entry
            try:
                self.bot.send_message(chat_id=self.chat_id, text=log_entry)
            except Exception:
                logging.error(
                    'Не удалось отправить сообщение об ошибке в Telegram'
                )


def validate_type(data, expected_type):
    """Проверяет, что переменная имеет ожидаемый тип."""
    if not isinstance(data, expected_type):
        error_message = (
            f'Ошибка валидации: ожидался {expected_type}, '
            f'но получен {type(data).__name__}: {data}'
        )
        logging.error(error_message)
        raise TypeError(error_message)


def validate_keys(data, required_keys, name):
    """Проверяет наличие всех обязательных ключей в словаре."""
    missing_keys = required_keys - data.keys()
    if missing_keys:
        error_message = (
            f'В {name} отсутствуют ключи: {", ".join(missing_keys)}'
        )
        logging.error(error_message)
        raise KeyError(error_message)


def check_unexpected_keys(item):
    """Проверяет наличие необязательных ключей и их типы."""
    item_keys = set(item.keys())
    unexpected_keys = item_keys - REQUIRED_KEYS
    if unexpected_keys:
        for key in unexpected_keys:
            if key in HOMEWORK_TYPES:
                validate_type(item[key], HOMEWORK_TYPES[key])


def check_status(item, index=None, raise_error=True):
    """Проверяет статус домашней работы."""
    if item['status'] not in HOMEWORK_VERDICTS:
        error_message = (
            f'Недопустимое значение статуса для '
            f'домашней работы "{item["homework_name"]}". '
            f'Ожидалось одно из: {set(HOMEWORK_VERDICTS.keys())}, '
            f'получено: {item["status"]}.'
        )
        logging.error(error_message)
        if raise_error:
            raise ValueError(error_message)
        else:
            return error_message


def check_date_updated(item):
    """Проверяет правильность формата даты."""
    try:
        if 'date_updated' in item:
            datetime.strptime(item['date_updated'], DATE_FORMAT)
    except ValueError:
        error_message = (
            f"Дата - {item['date_updated']} "
            f"не соответствует формату - {DATE_FORMAT}"
        )
        logging.error(error_message)
        raise ValueError(error_message)


def check_current_date_type(response):
    """Проверяет тип current_date."""
    current_date = response[RESPONSE_KEYS['CURRENT_DATE']]
    validate_type(current_date, (int, float))
    if current_date < 0:
        error_message = f'{current_date} не может быть отрицательным числом'
        logging.error(error_message)
        raise ValueError(error_message)
    try:
        datetime.fromtimestamp(current_date)
    except (ValueError, OSError):
        error_message = (
            f'Невозможно преобразовать значение - {current_date} '
            f'в валидный Unix timestamp.'
        )
        logging.error(error_message)
        raise ValueError(error_message)
