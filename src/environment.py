from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class TelegramSettings(BaseSettings, env_prefix='telegram_'):
    token: str = Field(..., env="TELEGRAM_TOKEN")


class DatabaseSettings(BaseSettings, env_prefix='database_'):
    engine: str = Field(default='sqlite')
    name: str = Field(default='db.sqlite3')
    host: Optional[str] = Field(default=None)
    port: Optional[int] = Field(default=None)
    user: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None)

    @property
    def url(self) -> str:
        if self.engine == 'sqlite':
            return f"sqlite+aiosqlite:///{self.name}"
        elif self.engine == 'postgresql':
            return (
                f"postgresql+asyncpg://{self.user}:{self.password}"
                f"@{self.host}:{self.port}/{self.name}"
            )

        return (
            f"{self.engine}://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )


class Settings(BaseSettings):
    base_url: str = Field(..., env="BASE_URL")
    max_user_groups: int = Field(default=5, env="MAX_USER_GROUPS")
    log_dir: Path = Field(default=Path("logs"), env="LOG_DIR")
    webapp_url: str = Field(..., env="WEBAPP_URL")
    telegram: TelegramSettings = TelegramSettings()
    database: DatabaseSettings = DatabaseSettings()
