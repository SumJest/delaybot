from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from database.models import Chat


class ChatRepository(SQLAlchemyAsyncRepository[Chat]):
    model_type = Chat
