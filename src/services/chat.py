from vkwave.api import APIOptionsRequestContext
from vkwave.bots import SimpleBotEvent, ForWhat, FiniteStateMachine

import settings
from models import User, Chat
from resources import messages
from middlewares.types.states import AddGroupStates


class ChatService:

    def __init__(self, api_context: APIOptionsRequestContext, fsm: FiniteStateMachine):
        self.api_context = api_context
        self.fsm = fsm

    async def create_chat(self, event: SimpleBotEvent, user: User, chat: Chat):
        if user.chats.count() > settings.MAX_USER_GROUPS:
            await self.api_context.messages.send(
                user_id=user.user_id,
                message=messages.MAX_GROUP_REACHED,
                random_id=0
            )
        chat.owner = user
        chat.save()
        await self.api_context.messages.send(
            user_id=user.user_id,
            message=messages.ADD_GROUP
        )
        await self.fsm.set_state(event=event, state=AddGroupStates.NAMING, for_what=ForWhat.FOR_USER)

    async def name_chat(self, event: SimpleBotEvent, user: User, chat: Chat):
        name = event.object.object.message.text
        chat.name = name
        chat.save()
        await self.fsm.finish(event=event, for_what=ForWhat.FOR_USER)

