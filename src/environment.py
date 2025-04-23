from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class VKSettings(BaseSettings, env_prefix='vk_'):
    token: str = Field(..., env="VK_TOKEN")
    group_id: int = Field(..., env="VK_GROUP_ID")


class TelegramSettings(BaseSettings, env_prefix='telegram_'):
    token: str = Field(..., env="TELEGRAM_TOKEN")


class Settings(BaseSettings):
    base_url: str = Field(..., env="BASE_URL")
    max_user_groups: int = Field(default=5, env="MAX_USER_GROUPS")
    log_dir: Path = Field(default=Path("logs"), env="LOG_DIR")
    vk: VKSettings = VKSettings()
    telegram: TelegramSettings = TelegramSettings()
