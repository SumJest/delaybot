# from vkwave.api import APIOptionsRequestContext
# from vkwave.bots import SimpleBotEvent, ForWhat, FiniteStateMachine
from aiogram import Bot
from aiogram.types import Message

import settings
from database.models import User, Chat
from resources import messages
# from middlewares.types.states import AddGroupStates


class ChatService:

    def __init__(self, bot: Bot, fsm):
        self.bot = bot
        self.fsm = fsm

    async def create_chat(self, event, user: User, chat: Chat):
        if user.chats.count() > settings.MAX_USER_GROUPS:
            await self.bot.send_message(
                chat_id=user.user_id,
                text=messages.MAX_GROUP_REACHED
            )
        chat.owner = user
        chat.save()
        await self.bot.send_message(
            chat_id=user.user_id,
            text=messages.ADD_GROUP
        )
        # await self.fsm.set_state(event=event, state=AddGroupStates.NAMING, for_what=ForWhat.FOR_USER)

    async def name_chat(self, event: Message, user: User, chat: Chat):
        name = event.text
        chat.name = name
        chat.save()
        # await self.fsm.finish(event=event, for_what=ForWhat.FOR_USER)

