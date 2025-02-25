from peewee import IntegerField, BooleanField, CharField

from .base import BaseModel


class User(BaseModel):
    user_id = IntegerField(primary_key=True)
    is_blocked = BooleanField(default=False)
    is_admin = BooleanField(default=False)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    username = CharField(null=True)

    def __str__(self):
        if self.first_name or self.last_name:
            return f'{self.first_name or ""} {self.last_name or ""}'.strip()
        elif self.username:
            return f'@{self.username}'
        else:
            return f'[{self.user_id}]'
