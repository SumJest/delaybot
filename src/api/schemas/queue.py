from datetime import datetime

from api.schemas.base import BaseModel
from api.schemas.user import UserSchema


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


class DetailQueueSchema(QueueSchema):
    members: list[UserSchema]


class UpdateQueueSchema(BaseModel):
    name: str | None = None
    closed: bool | None = None
    members: list[int] | None = None


class QueueShareSchema(BaseModel):
    id: int
    queue_id: int
    token: str
    can_manage: bool
    expires_at: datetime

    created_at: datetime
    updated_at: datetime


class CreateQueueShareSchema(BaseModel):
    queue_id: int
    can_manage: bool = False


class ActivateQueueShareSchema(BaseModel):
    token: str
