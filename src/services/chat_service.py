from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from database.repository.chat import ChatRepository


class ChatService(SQLAlchemyAsyncRepositoryService[ChatRepository]):
    repository = ChatRepository
