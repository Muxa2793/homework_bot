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
    BotSendMeassageException,
    HomeworkCheckException,
    EndpointNotAccessException,
    TokenNoExistException,
)

load_dotenv()

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


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 6
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправка сообщения пользователю с chat_id=TELEGRAM_CHAT_ID."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f'Бот отправил сообщение: {message}')
    except Exception:
        raise BotSendMeassageException()


def get_api_answer(current_timestamp):
    """Отправка GET запроса на url=ENDPOINT."""
    logger.info('Запрос отправлен')

    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    api_answer = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if api_answer.status_code != HTTPStatus.OK:
        raise EndpointNotAccessException(ENDPOINT)
    return api_answer.json()


def check_response(response):
    """Проверка данных в ответе."""
    if type(response) != dict:
        raise TypeError
    homework = response['homeworks']
    if isinstance(homework, list):
        return homework
    raise HomeworkCheckException()


def parse_status(homework):
    """Получение данных по текущему домашнему заданию."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES[homework_status]
    message = ('Изменился статус проверки работы '
               f'"{homework_name}". {verdict}')
    return message


def check_tokens():
    """Проверка токенов."""
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        return True
    logger.critical('Отсутствуют переменные окружения')
    return False


def check_homework_status(message, homework_status):
    """Проверка изменения статуса домашнего задания.

    Сравнивается значение полученное в предыдущем запросе с текущим

    """
    if message == homework_status:
        logger.info('Статус задания не изменился')
        return False
    return True


def main():
    """Основная логика работы бота."""
    if check_tokens():
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        delta = timedelta(minutes=10).total_seconds()
        current_timestamp = int(time.time() - delta)
    else:
        raise TokenNoExistException()

    while True:
        try:
            api_answer = get_api_answer(current_timestamp)
            check_response(api_answer)
            homework = api_answer['homeworks']
            if homework:
                message = parse_status(homework[0])
            else:
                logger.info('Статус не изменился')
                time.sleep(RETRY_TIME)
                continue
            send_message(bot, message)
            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
