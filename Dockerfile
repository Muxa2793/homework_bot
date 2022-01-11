FROM python:3.8

WORKDIR /homework_bot

COPY . .

RUN apt-get update
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

CMD [ "python3", "bot.py" ]
