from datetime import datetime

from advanced_alchemy.base import DefaultBase
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column


class BaseModel(DefaultBase):
    __abstract__ = True
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
