import logging

logger = logging.getLogger(__name__)

file_log = logging.FileHandler("app.log")
console_out = logging.StreamHandler()

logging.basicConfig(
    handlers=(file_log, console_out),
    level=logging.INFO,
    format="%(asctime)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s",
    datefmt="%d.%m.%Y %H:%M:%S",
)

formatter = logging.Formatter(
    "%(asctime)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s",
    datefmt="%d.%m.%Y %H:%M:%S",
)
console_out.setFormatter(formatter)

logger.addHandler(console_out)
