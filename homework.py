import os
import time
import logging

import requests
import telegram

from datetime import timedelta
from http import HTTPStatus
from logging import Formatter, StreamHandler
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv

from exception import (
    HomeworkCheckException,
    EndpointDataIsEmptyException,
    EndpointNotAccessException,
    TokenNoExistException,
)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

handler = RotatingFileHandler(
    filename='homework.log',
    maxBytes=5242880,
    backupCount=1,
)
handler.setFormatter(formatter)

stream_handler = StreamHandler()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.addHandler(stream_handler)


def send_message(bot, message):
    """Отправка сообщения пользователю с chat_id=TELEGRAM_CHAT_ID."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f'Бот отправил сообщение: {message}')
    except Exception:
        logger.error(
            'Сообщение не доставлено, проверьте работу телеграмм сервисов.'
        )


def get_api_answer(current_timestamp):
    """Отправка GET запроса на url=ENDPOINT."""
    logger.info('Запрос отправлен')

    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        api_answer = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except Exception:
        raise EndpointNotAccessException(ENDPOINT)
    if api_answer.status_code != HTTPStatus.OK:
        raise EndpointNotAccessException(ENDPOINT)
    if api_answer:
        return api_answer.json()
    raise EndpointDataIsEmptyException(ENDPOINT)


def check_response(response):
    """Проверка данных в ответе."""
    if not isinstance(response, dict):
        raise TypeError
    try:
        homework = response['homeworks']
    except KeyError:
        raise KeyError
    if not isinstance(homework, list):
        raise HomeworkCheckException()
    return homework


def parse_status(homework):
    """Получение данных по текущему домашнему заданию."""
    homework_name = homework.get('homework_name', None)
    homework_status = homework.get('status', None)
    if not homework_name and not homework_status:
        raise HomeworkCheckException()
    try:
        verdict = HOMEWORK_VERDICTS[homework_status]
    except KeyError:
        raise KeyError
    message = ('Изменился статус проверки работы '
               f'"{homework_name}". {verdict}')
    return message


def check_tokens():
    """Проверка токенов."""
    if all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        return True
    logger.critical('Отсутствуют переменные окружения')
    return False


def get_timestamp(api_answer):
    """Получение timestamp для отсчёта времени от последней проверки."""
    try:
        current_timestamp = api_answer['current_date']
    except KeyError:
        raise KeyError
    return current_timestamp


def check_error(error, previous_error, error_count):
    """Сравнение полученной ошибки с предыдущей."""
    if str(error) == previous_error and error_count != 5:
        return False
    return True


def main():
    """Основная логика работы бота."""
    # Проверяем наличие переменных окружения
    if check_tokens():
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        delta = timedelta(minutes=10).total_seconds()
        current_timestamp = int(time.time() - delta)
    else:
        raise TokenNoExistException()

    # Создаём пустую переменную предыдущей ошибки и счётчик ошибок
    previous_error = None
    error_count = 0

    while True:
        try:
            # Создаём запрос
            api_answer = get_api_answer(current_timestamp)
            # Проверяем ответ на соответствие ожиданию
            homework = check_response(api_answer)
            # Проверяем является ли список пустым, если да, то новый цикл
            if homework:
                message = parse_status(homework[0])
            else:
                logger.info('Статус не изменился')
                time.sleep(RETRY_TIME)
                continue
            # Отправляем пользователю сообщение
            send_message(bot, message)
            # Получем новое время отсчёта
            current_timestamp = get_timestamp(api_answer)
            # Ждём RETRY_TIME секунд до запуска нового цикла
            time.sleep(RETRY_TIME)
        except Exception as error:
            # Формируем сообщение об ошибке и увеличиваем счётчик ошибок
            message = f'Сбой в работе программы: {error}'
            error_count += 1
            logger.error(message)
            # Проверяем полученную ошибку с предыдущей
            if check_error(error, previous_error, error_count):
                previous_error = str(error)
                error_count = 0
                send_message(bot, message)
            # Ждём RETRY_TIME секунд до запуска нового цикла
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
