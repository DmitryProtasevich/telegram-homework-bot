import os


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
RESPONSE_KEYS = {
    'HOMEWORKS': 'homeworks',
    'CURRENT_DATE': 'current_date',
}
REQUIRED_KEYS = {'homework_name', 'status'}
OPTIONAL_KEYS = {'date_updated', 'id', 'lesson_name', 'reviewer_comment'}
HOMEWORK_TYPES = {
    'id': int,
    'homework_name': str,
    'reviewer_comment': str,
    'lesson_name': str,
    'status': str,
    'date_updated': str
}
DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}
INITIAL_TIMESTAMP = 0
