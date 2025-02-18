class MissingEnvironmentVariableError(Exception):
    """Ошибка: отсутствует обязательная переменная окружения."""

    pass


class RequestFailedError(Exception):
    """Ошибка: запрос не был выполнен."""

    pass


class UnexpectedAPIStatusError(Exception):
    """Ошибка: запрос к API завершился с неожиданным статусом."""

    pass


class InvalidJSONResponseError(Exception):
    """Ошибка: ответ API не является JSON."""

    pass
