from pydantic import BaseModel, Field


class UserFilter(BaseModel):
    id_: int | None = Field(default=None, alias="id")
    username: str | None = Field(default=None, min_length=4)
