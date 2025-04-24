from functools import cached_property

from aiogram import Bot, Dispatcher
from dependency_injector.wiring import inject, Provide

from bot.services import BotQueueService
from containers.bot import BotContainer
from services.chat_service import ChatService
from services.queue_service import QueueService, QueuePermissionService, QueueShareService
from services.user_service import UserService


# class ServicesContainer(containers.DeclarativeContainer):
#     bot = providers.Dependency()
#     fsm = providers.Dependency()
#     db = providers.Singleton(Database, db_url=database_url)
#     session = providers.Resource(SessionResource)
#     user_service = providers.Factory(
#         UserService,
#         session=session
#     )
#     chat_service = providers.Factory(
#         ChatService,
#         session=session
#     )
#     queue_service = providers.Factory(
#         QueueService,
#         session=session
#     )
#     bot_queue_service = providers.Factory(
#         BotQueueService,
#         bot=bot,
#         queue_service=queue_service,
#         user_service=user_service,
#         chat_service=chat_service
#     )


class ServicesContainer:

    @inject
    def __initialize_bot(self,
                         bot: Bot = Provide[BotContainer.bot],
                         dp: Dispatcher = Provide[BotContainer.dispatcher]):
        self.bot = bot
        self.dp = dp

    def __init__(self, session):
        self.session = session
        self.__initialize_bot()

    @cached_property
    def user_service(self) -> UserService:
        return UserService(self.session)

    @cached_property
    def chat_service(self) -> ChatService:
        return ChatService(self.session)

    @cached_property
    def queue_service(self) -> QueueService:
        return QueueService(self.session)

    @cached_property
    def queue_share_service(self) -> QueueShareService:
        return QueueShareService(self.session)

    @cached_property
    def queue_permission_service(self) -> QueuePermissionService:
        return QueuePermissionService(self.session)

    @cached_property
    def bot_queue_service(self):
        return BotQueueService(bot=self.bot,
                               queue_service=self.queue_service,
                               user_service=self.user_service,
                               chat_service=self.chat_service)
