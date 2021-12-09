class HomeworkCheckException(Exception):
    """Проверка доступности ключей в запросе."""

    def __init__(self):
        """Инициализация класса."""
        self.message = 'Полученные данные не соответствуют ожидаемым'
        super().__init__(self.message)

    def __str__(self):
        """Сообщение об ошибке."""
        return f'{self.message}'


class TokenNoExistException(Exception):
    """Проверка доступности переменных окружения."""

    def __init__(self):
        """Инициализация класса."""
        self.message = 'Переменные окружения недоступны'
        super().__init__(self.message)

    def __str__(self):
        """Сообщение об ошибке."""
        return f'{self.message}'


class EndpointNotAccessException(Exception):
    """Проверка доступности ednpoint'a."""

    def __init__(self, endpoint):
        """Инициализация класса."""
        self.endpoint = endpoint
        self.message = f'endpoint {endpoint} недоступен'
        super().__init__(self.message)

    def __str__(self):
        """Сообщение об ошибке."""
        return f'{self.message}'


class EndpointDataIsEmptyException(Exception):
    """Проверка доступности ednpoint'a."""

    def __init__(self, endpoint):
        """Инициализация класса."""
        self.endpoint = endpoint
        self.message = f'По ednpoint {endpoint} получены некорректные данные!'
        super().__init__(self.message)

    def __str__(self):
        """Сообщение об ошибке."""
        return f'{self.message}'


class StatusNotChangeException(Exception):
    """Проверка статуса endpoint'a."""

    def __init__(self, endpoint):
        """Инициализация класса."""
        self.endpoint = endpoint
        self.message = f'endpoint {endpoint} недоступен'
        super().__init__(self.message)

    def __str__(self):
        """Сообщение об ошибке."""
        return f'{self.message}'
