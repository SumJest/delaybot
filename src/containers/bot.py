from aiogram import Bot, Dispatcher, types
from dependency_injector import containers, providers


class BotContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    bot = providers.Singleton(Bot,
                              token=config.telegram.token)

    dispatcher = providers.Singleton(Dispatcher)

    bot_info = providers.Object()
