from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from database.models import Chat
from database.repository.chat import ChatRepository


class ChatService(SQLAlchemyAsyncRepositoryService[Chat, ChatRepository]):
    repository_type = ChatRepository
