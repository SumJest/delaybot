from sqlalchemy import event, UniqueConstraint, Index
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, BigInteger, Sequence, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship, Mapped, mapped_column
from database.models.basemodel import BaseModel
from database.fields.list_field import ListField  # Custom field for handling lists (as JSON)
from database.models.chat import Chat  # Assuming Chat model is in a separate file
from database.models.user import User  # Assuming User model is in a separate file


class Queue(BaseModel):
    __tablename__ = 'queue'  # Table name in the database

    # Columns
    id = Column(BigInteger, primary_key=True, autoincrement=True)  # Primary key
    name = Column(String(255), nullable=False)  # String field with max length 255
    chat_id = Column(BigInteger, ForeignKey('chat.id', ondelete="CASCADE"))  # ForeignKey to Chat
    msg_id = Column(Integer, nullable=True)  # Integer field
    owner_id = Column(BigInteger, ForeignKey('user.id', ondelete="CASCADE"))  # ForeignKey to User
    closed = Column(Boolean, default=False)  # Boolean field with default False
    members = Column(MutableList.as_mutable(JSONB), default=[])  # Custom ListField for storing lists as JSON

    # Relationships
    chat = relationship('Chat', back_populates="queues")  # Relationship to Chat
    owner = relationship('User', back_populates="queues")  # Relationship to User
    shares = relationship('QueueShare', back_populates='queue')
    permissions = relationship('QueuePermission', back_populates='queue')

class QueueShare(BaseModel):
    __tablename__ = 'queue_share'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    queue_id = Column(BigInteger, ForeignKey('queue.id', ondelete="CASCADE"))
    token = Column(String(32), unique=True, index=True)       # 6–8 символов
    can_manage = Column(Boolean, default=False)                # право управлять очередью
    expires_at: Mapped[datetime] = mapped_column()

    queue = relationship('Queue', back_populates='shares')

class QueuePermission(BaseModel):
    __tablename__ = 'queue_permission'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    queue_id = Column(BigInteger, ForeignKey('queue.id', ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    can_manage = Column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint('queue_id', 'user_id', name='uq_queue_user'),
        Index('ix_queue_permission_user_id', 'user_id'),
        Index('ix_queue_permission_queue_id', 'queue_id'),
    )

    # relationships (если ещё не было)
    queue = relationship('Queue', back_populates='permissions')
    user = relationship('User', back_populates='permissions')





@event.listens_for(Session, 'do_orm_execute')
def apply_expired_filter(execute_state):
    if (
        execute_state.is_select
        and not execute_state.is_column_load
        and not execute_state.is_relationship_load
    ):
        if QueueShare.__mapper__ in execute_state.all_mappers:
            if not execute_state.execution_options.get('include_expired', False):
                current_time = datetime.now(timezone.utc)
                condition = QueueShare.expires_at > current_time
                execute_state.statement = execute_state.statement.where(condition)