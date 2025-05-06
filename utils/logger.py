import logging
import os
from logging.handlers import TimedRotatingFileHandler
import config

os.makedirs('logs', exist_ok=True)

app_logger = logging.getLogger('pdf_app')
app_logger.setLevel(config.LOG_LEVEL)

# Timed rotating file handler: daily rotation, keep 30 days, with suffix in filename
file_handler = TimedRotatingFileHandler('logs/app.log', when='midnight', interval=1,
                                        backupCount=config.LOG_BACKUP_COUNT, encoding='utf-8', utc=True)
file_handler.suffix = '%Y-%m-%d'
file_formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
console_handler.setFormatter(console_formatter)

app_logger.addHandler(file_handler)
app_logger.addHandler(console_handler)


def log_info(message):
    app_logger.info(message)


def log_warning(message):
    app_logger.warning(message)


def log_error(message):
    app_logger.error(message)


def log_debug(message):
    app_logger.debug(message)


def log_critical(message):
    app_logger.critical(message)
