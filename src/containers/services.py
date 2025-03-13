from dependency_injector import containers, providers
from bot.services import BotQueueService
from containers.context_manager_provider import AsyncContextManager
from database.connection import Database, database_url, SessionResource
from services.user_service import UserService
from services.chat_service import ChatService


class ServicesContainer(containers.DeclarativeContainer):
    bot = providers.Dependency()
    fsm = providers.Dependency()
    db = providers.Singleton(Database, db_url=database_url)
    session = providers.Resource(SessionResource)
    queue_service = providers.Factory(
        BotQueueService,
        bot=bot
    )
    user_service = providers.Factory(
        UserService,
        session=session
    )
    chat_service = providers.Factory(
        ChatService,
        session=session
    )
