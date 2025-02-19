class MissingEnvironmentVariableError(Exception):
    """Ошибка: отсутствует обязательная переменная окружения."""


class EmptyResponseFromAPI(Exception):
    """Ошибка: пустой ответ API."""


class InvalidResponseCode(Exception):
    """Не верный код ответа."""
