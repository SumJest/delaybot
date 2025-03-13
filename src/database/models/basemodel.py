from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, Query

from database.connection import connection, async_session_maker
from advanced_alchemy.base import DefaultBase


class BaseModel(DefaultBase):
    __abstract__ = True
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
