import logging

from logging import Formatter, StreamHandler
from logging.handlers import RotatingFileHandler

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
