from sqlalchemy import Column, BigInteger, Text, ForeignKey
from sqlalchemy.orm import relationship
from database.models.basemodel import BaseModel
from database.models.user import User  # Assuming User model is in a separate file


class Chat(BaseModel):
    __tablename__ = 'chat'  # Table name in the database

    # Columns
    id = Column(BigInteger, primary_key=True)  # Primary key (BigInteger)
    name = Column(Text, default="")  # Text field with default empty string
    owner_id = Column(BigInteger, ForeignKey('user.id', ondelete="SET NULL"), nullable=True, default=None)  # ForeignKey to User

    # Relationships
    owner = relationship('User', back_populates="chats")  # Relationship to User
    queues = relationship('Queue', back_populates="chat")

