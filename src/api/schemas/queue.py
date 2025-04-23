from datetime import datetime

from api.schemas.base import BaseModel


class QueueSchema(BaseModel):
    id: int
    name: str
    chat_id: int
    msg_id: int | None
    owner_id: int
    closed: bool
    members: list[int]
    created_at: datetime
    updated_at: datetime
