# homework_bot

Телеграм бот, написанный на языке программирования [Python](https://www.python.org), предназначен для получения уведомлений о статусе прохождения вашего домашнего задания.

## Запуск

- склонируйте репозиторий

```bash
git clone https://github.com/Muxa2793/homework_bot
```

- в корне проекта создайте и активируйте виртуальное окружение

```bash
python3 -m venv venv
source venv/bin/activate
```

- установите зависимости

```bash
pip install -r requirements.txt
```

- создайте файл .env и добавьте в него следующие переменные:

```bash
PRACTICUM_TOKEN = <ваш токен на яндекс практикуме>
TELEGRAM_TOKEN = <токен вашего телеграм бота>
TELEGRAM_CHAT_ID = <id чата, в который вы хотите посылать сообщения>
```

## Дополнительно

- Запросы на `endpoint` Яндекса делаются каждые 10 минут, чтобы изменить интвервал запросов необходимо изменить значение переменной `RETRY_TIME` в секундах;
- [Как создать своего телеграм бота](https://core.telegram.org/bots#3-how-do-i-create-a-bot);
- Узнать id чата можно с помощью [инфобота](https://t.me/userinfobot);
- [Получить токен](https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a) для получения доступа к API Яндекс.Практикума можно только если вы являетесь студентом платформы;

## Авторы

Команда [Яндекс.Практикума](http://example.com/ "Яндекс.Практикум") и [Михаил Спиридонов](https://t.me/MikhailSpiridonov "Мой Telegram для связи").

## License

MIT
