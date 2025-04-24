import logging
from pathlib import Path

from environment import Settings

BASE_DIR = Path(__file__).resolve().parent

settings = Settings()

BASE_URL = settings.base_url.rstrip('/')
VK_TOKEN = settings.vk.token
VK_GROUP_ID = settings.vk.group_id
TELEGRAM_TOKEN = settings.telegram.token
MAX_USER_GROUPS = settings.max_user_groups
LOG_DIR = settings.log_dir

logging.basicConfig(level=logging.INFO)
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

# logging.basicConfig(
#     handlers=[RotatingFileHandler(
#         LOG_DIR / 'delaybot.log',
#         maxBytes=100000,
#         backupCount=10,
#     )],
#     level=logging.INFO
# )
