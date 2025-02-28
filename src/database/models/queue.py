from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from database.models.base import Base
from database.fields.list_field import ListField  # Custom field for handling lists (as JSON)
from database.models.chat import Chat  # Assuming Chat model is in a separate file
from database.models.user import User  # Assuming User model is in a separate file


class Queue(Base):
    __tablename__ = 'queue'  # Table name in the database

    # Columns
    id = Column(BigInteger, primary_key=True)  # Primary key
    name = Column(String(255), nullable=False)  # String field with max length 255
    chat_id = Column(BigInteger, ForeignKey('chat.id', ondelete="CASCADE"))  # ForeignKey to Chat
    msg_id = Column(Integer, nullable=False)  # Integer field
    owner_id = Column(BigInteger, ForeignKey('user.id', ondelete="CASCADE"))  # ForeignKey to User
    closed = Column(Boolean, default=False)  # Boolean field with default False
    members = Column(ListField, default=[])  # Custom ListField for storing lists as JSON

    # Relationships
    chat = relationship(Chat, back_populates="queues")  # Relationship to Chat
    owner = relationship(User, back_populates="queues")  # Relationship to User
