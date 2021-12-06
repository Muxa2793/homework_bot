import logging

logging.basicConfig(
    level=logging.DEBUG,
    filename='homework.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
    filemode='w',
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
