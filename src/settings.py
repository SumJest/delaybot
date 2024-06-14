import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import smart_getenv

BASE_DIR = Path(__file__).resolve().parent

VK_TOKEN = smart_getenv.getenv("VK_TOKEN", type=str)
VK_GROUP_ID = smart_getenv.getenv("VK_GROUP_ID", type=int)

MAX_USER_GROUPS = smart_getenv.getenv("MAX_USER_GROUPS", type=int, default=5)
LOG_DIR = Path(smart_getenv.getenv("LOG_DIR", type=str, default=BASE_DIR / 'logs'))


logging.basicConfig(
    handlers=[RotatingFileHandler(
        LOG_DIR / 'delaybot.log',
        maxBytes=100000,
        backupCount=10,
    )],
    level=logging.INFO
)
