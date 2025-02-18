import logging
import sys
import time
from http.client import OK

import requests
from dotenv import load_dotenv
import telebot

from constants import (
    ENDPOINT, HEADERS, HOMEWORK_VERDICTS,
    INITIAL_TIMESTAMP, PRACTICUM_TOKEN, REQUIRED_KEYS, RESPONSE_KEYS,
    RETRY_PERIOD, TELEGRAM_CHAT_ID, TELEGRAM_TOKEN
)
from exceptions import (
    MissingEnvironmentVariableError,
    RequestFailedError, UnexpectedAPIStatusError
)
from utils import (
    TelegramErrorHandler,
    check_current_date_type, check_date_updated, check_status,
    check_unexpected_keys, validate_keys, validate_type
)

load_dotenv()


def configure_logging(bot):
    """Настройка логирования."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - [%(levelname)s] - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('errors.log'),
            TelegramErrorHandler(bot, TELEGRAM_CHAT_ID)
        ]
    )


def check_tokens():
    """Проверяет доступность переменных окружения."""
    for var_name, var_value in {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }.items():
        if not var_value:
            error_message = (
                f'Отсутствует обязательная переменная '
                f'окружения - {var_name}'
            )
            logging.critical(error_message)
            raise MissingEnvironmentVariableError(error_message)


def get_api_answer(timestamp):
    """Делает запрос к API-сервису и возвращает ответ в формате Python."""
    try:
        response = requests.get(
            ENDPOINT, headers=HEADERS, params={'from_date': timestamp}
        )
        if response.status_code != OK:
            error_message = (
                f'Ошибка: запрос к API завершился с неожиданным статусом. '
                f'Ожидался - OK, получен - {response.status_code}.'
            )
            logging.error(error_message)
            raise UnexpectedAPIStatusError(error_message)
        try:
            return response.json()
        except ValueError:
            error_message = 'Ответ API не является JSON'
            logging.error(error_message)
            raise ValueError
    except requests.exceptions.RequestException:
        error_message = 'Запрос к API не был выполнен'
        logging.error(error_message)
        raise RequestFailedError(error_message)


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    validate_type(response, dict)
    validate_keys(response, {
        RESPONSE_KEYS['HOMEWORKS'], RESPONSE_KEYS['CURRENT_DATE']
    }, 'response')
    validate_type(response[RESPONSE_KEYS['HOMEWORKS']], list)
    if response.get(RESPONSE_KEYS['HOMEWORKS']):
        for index, item in enumerate(response[RESPONSE_KEYS['HOMEWORKS']]):
            validate_type(item, dict)
            validate_keys(item, REQUIRED_KEYS, f'homework[{index}]')
            check_unexpected_keys(item)
            check_status(item, index)
            check_date_updated(item)
    check_current_date_type(response)


def populate_statuses_dict(response, statuses):
    """Наполняет словарь названиями и статусами работ."""
    if RESPONSE_KEYS['HOMEWORKS'] in response:
        for homework in response['homeworks']:
            statuses[homework.get('id')] = homework.get('status')
    return statuses


def parse_status(homework):
    """
    Извлекает информацию из конкретной домашней работы.
    Возвращает подготовленную для отправки в Telegram строку.
    """
    validate_keys(homework, REQUIRED_KEYS, 'homework')
    check_status(homework, raise_error=True)
    return (
        f'Изменился статус проверки работы "{homework["homework_name"]}". '
        f'{HOMEWORK_VERDICTS[homework["status"]]}'
    )


def check_status_changes(response, initial_statuses):
    """
    Проверяет изменения статусов домашних работ.
    Вносит изменения в initial_statuses.
    Возвращает список работ с измененным статусом.
    Также проверяет дату последнего обновления работы.
    """
    changed_homeworks = []
    for homework in response[RESPONSE_KEYS['HOMEWORKS']]:
        homework_name = homework.get('homework_name')
        current_status = homework.get('status')
        last_updated = homework.get('date_updated')
        if homework_name in initial_statuses:
            cached_status, cached_date_updated = (
                initial_statuses[homework_name]
            )
            if (
                cached_status != current_status or cached_date_updated
            ) != last_updated:
                (
                    initial_statuses[homework_name]
                ) = current_status, last_updated
                changed_homeworks.append(homework)
        else:
            initial_statuses[homework_name] = (current_status, last_updated)
            changed_homeworks.append(homework)
    return changed_homeworks


def send_message(bot, message):
    """Отправляет сообщение в Telegram-чат."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )
        logging.debug(f'Сообщение успешно отправлено в Telegram: {message}')
    except Exception as error:
        logging.error(f'Ошибка при отправке сообщения в Telegram: {error}')


def main():
    """Основная логика работы бота."""
    bot = telebot.TeleBot(token=TELEGRAM_TOKEN)
    configure_logging(bot)
    check_tokens()
    initial_statuses = dict()
    timestamp = int(time.time())
    response = get_api_answer(INITIAL_TIMESTAMP)
    check_response(response)
    populate_statuses_dict(response, initial_statuses)

    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            if response[RESPONSE_KEYS['HOMEWORKS']]:
                changed_homeworks = check_status_changes(
                    response, initial_statuses
                )
                for homework in changed_homeworks:
                    message = parse_status(homework)
                    send_message(bot, message)
            else:
                logging.debug(
                    'Отсутствуют новые статусы домашних работ в ответе API.'
                )
            timestamp = response[RESPONSE_KEYS['CURRENT_DATE']]
        except Exception as error:
            logging.error(f'Сбой в работе программы: {error}')
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
