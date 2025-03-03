from sqlalchemy import Column, BigInteger, Boolean, String, Sequence
from sqlalchemy.orm import relationship

from database.models.basemodel import BaseModel


class User(BaseModel):
    __tablename__ = 'user'

    # Columns
    id = Column(BigInteger, primary_key=True)
    is_blocked = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    username = Column(String, nullable=True)

    # relationships
    chats = relationship('Chat', back_populates='owner')
    queues = relationship('Queue', back_populates='owner')

    def __str__(self):
        if self.first_name or self.last_name:
            return f'{self.first_name or ""} {self.last_name or ""}'.strip()
        elif self.username:
            return f'@{self.username}'
        else:
            return f'[{self.user_id}]'
