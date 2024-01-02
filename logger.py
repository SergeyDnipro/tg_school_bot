import logging
from logging import handlers

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
main_logger = logging.getLogger(__name__)
main_logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(asctime)s] - %(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %H:%M:%S')

console_handler = logging.StreamHandler()
file_handler = logging.handlers.RotatingFileHandler('myLog.log', mode='a', maxBytes=10000)

console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

main_logger.addHandler(console_handler)
main_logger.addHandler(file_handler)
