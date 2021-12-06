import os
import time

import requests
import telegram

from datetime import timedelta
from http import HTTPStatus

from dotenv import load_dotenv

from exception import (
    BotSendMeassageException,
    EndpointNotAccessException,
    HomeworkKeyException,
    TokenNoExistException,
)
from logger import logger

load_dotenv()

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
    return api_answer


def check_response(response):
    """Проверка статуса ответа на запрос."""
    if response.status_code == HTTPStatus.OK:
        return True
    raise EndpointNotAccessException(ENDPOINT)


def parse_status(homework):
    """Получение данных по текущему домашнему заданию."""
    try:
        if len(homework['homeworks']) == 0:
            message = 'Домашняя работа ещё не была отправлена на проверку'
            logger.info(message)
            return False
        homework_name = homework['homeworks'][0]['homework_name']
        homework_status = homework['homeworks'][0]['status']
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    except KeyError as error:
        key = error.args[0]
        raise HomeworkKeyException(key)


def check_tokens():
    """Проверка токенов."""
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        return True
    logger.critical('Отсутствуют переменные окружения')
    raise TokenNoExistException()


def check_homework_status(message, homework_status):
    """Проверка изменения статуса домашнего задания.

    Сравнивается значение полученное в предыдущем запросе с текущим

    """
    if message == homework_status:
        print(message)
        logger.info('Статус задания не изменился')
        return False
    return True


def main():
    """Основная логика работы бота."""
    check_tokens()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    delta = timedelta(days=20).total_seconds()
    current_timestamp = int(time.time() - delta)
    homework_status = ''

    while True:
        try:
            api_answer = get_api_answer(current_timestamp)
            check_response(api_answer)
            homework = api_answer.json()
            message = parse_status(homework)
            # Проверяем сообщение и статус домашнего задания
            if message and check_homework_status(message, homework_status):
                homework_status = message
                send_message(bot, message)
            else:
                time.sleep(RETRY_TIME)
                continue
            current_timestamp = int(time.time() - delta)
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            # Отправляем сообщение о сбое создателю бота
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
