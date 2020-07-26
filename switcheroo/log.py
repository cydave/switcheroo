import logging
import queue
from logging.handlers import QueueHandler, QueueListener
from switcheroo.config import Config

from arrow.arrow import Arrow


class ArrowTimeFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        arrow_time = Arrow.fromtimestamp(record.created)
        return arrow_time.isoformat()


def setup_logging():
    logger = logging.getLogger("switcheroo")
    log_queue = queue.Queue(-1)
    queue_handler = QueueHandler(log_queue)
    logger.addHandler(queue_handler)
    logger.setLevel(logging.INFO)
    fmt = ArrowTimeFormatter(fmt="%(asctime)s %(message)s")
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)
    console_handler.setLevel(logging.INFO)
    if Config.LOGFILE:
        file_handler = logging.FileHandler(filename=Config.LOGFILE, mode="a")
        file_handler.setFormatter(fmt)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        listener = QueueListener(log_queue, console_handler, file_handler)
    else:
        listener = QueueListener(log_queue, console_handler)
    listener.start()
    return logger, listener
