import logging
import sys
import time
from http.client import OK

import requests
from dotenv import load_dotenv
import telebot

from constants import (
    ENDPOINT, HEADERS, HOMEWORK_VERDICTS,
    PRACTICUM_TOKEN, REQUIRED_KEYS,
    RETRY_PERIOD, TELEGRAM_CHAT_ID, TELEGRAM_TOKEN
)
from exceptions import (
    EmptyResponseFromAPI,
    InvalidResponseCode,
    MissingEnvironmentVariableError,
)


load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - [%(levelname)s] - %(message)s - Line: %(lineno)d',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(__file__ + '.log', encoding='utf-8'),
    ]
)


def check_tokens():
    """Проверяет доступность переменных окружения."""
    tokens = (
        ('PRACTICUM_TOKEN', PRACTICUM_TOKEN),
        ('TELEGRAM_TOKEN', TELEGRAM_TOKEN),
        ('TELEGRAM_CHAT_ID', TELEGRAM_CHAT_ID)
    )
    missing_tokens = []
    for var_name, var_value in tokens:
        if not var_value:
            logging.critical(
                f'Отсутствует обязательная переменная '
                f'окружения - {var_name}'
            )
            missing_tokens.append(var_name)
    if missing_tokens:
        raise MissingEnvironmentVariableError(
            f'Отсутствует(ют) обязательная(ые) переменная(ые) '
            f'окружения - {", ".join(missing_tokens)}')


def get_api_answer(timestamp):
    """Делает запрос к API-сервису и возвращает ответ в формате Python."""
    api_request_params = {
        'url': ENDPOINT,
        'headers': HEADERS,
        'params': {'from_date': timestamp}
    }
    logging.info(
        'Начат запрос к API. url - {url},'
        'Заголовки - {headers},'
        'Параметры - {params}'.format(**api_request_params))
    try:
        statuses_homework = requests.get(**api_request_params)
    except requests.exceptions.RequestException:
        raise ConnectionError(
            'Не верный код ответа: url - {url},'
            'headers - {headers},'
            'params - {params}'.format(**api_request_params)
        )
    if statuses_homework.status_code != OK:
        raise InvalidResponseCode(
            f'Не удалось получить ответ API, '
            f'ошибка - {statuses_homework.status_code} '
            f'причина - {statuses_homework.reason} '
            f'текст - {statuses_homework.text}')
    return statuses_homework.json()


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    logging.info('Проверка ответа API началась')
    if not isinstance(response, dict):
        raise TypeError('Ошибка: ответ API должен быть словарем.')
    if 'homeworks' not in response:
        raise EmptyResponseFromAPI(
            'Ошибка: в ответе API отсутствует ключ - homeworks'
        )
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError(
            'Ошибка: значение ключа - homeworks должно быть списком.'
        )
    return homeworks


def parse_status(homework):
    """
    Извлекает информацию из конкретной домашней работы.
    Возвращает подготовленную для отправки в Telegram строку.
    """
    for key in REQUIRED_KEYS:
        if REQUIRED_KEYS[key] not in homework:
            raise KeyError(f'Отсутствует ключ: {REQUIRED_KEYS[key]}')
    homework_status = homework.get(REQUIRED_KEYS['STATUS'])
    if homework_status not in HOMEWORK_VERDICTS:
        raise ValueError(f'Неизвестный статус работы - {homework_status}')
    return (
        f'Изменился статус проверки работы '
        f'"{homework.get(REQUIRED_KEYS["HOMEWORK_NAME"])}". '
        f'{HOMEWORK_VERDICTS[homework_status]}'
    )


def send_message(bot, message):
    """Отправляет сообщение в Telegram-чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logging.error(f'Ошибка при отправке сообщения в Telegram: {error}')
        return False
    logging.debug(f'Сообщение успешно отправлено в Telegram: {message}')
    return True


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = telebot.TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    last_message = ''
    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if not homeworks:
                logging.debug(
                    'Отсутствуют новые статусы домашних работ в ответе API.'
                )
                continue
            homework = homeworks[0]
            message = parse_status(homework)
            logging.debug(f'Текущий статус: {message}')
            if message != last_message and send_message(bot, message):
                last_message = message
                timestamp = response.get('current_date', timestamp)
        except Exception as error:
            logging.exception('Сбой в работе программы')
            error_message = f'Сбой в работе программы: {error}'
            if (error_message != last_message
                    and send_message(bot, error_message)):
                last_message = error_message
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
