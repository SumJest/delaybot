from vkwave.api import APIOptionsRequestContext
from vkwave.bots import SimpleBotEvent

from models import User
from resources import messages
from utils.keyboard import main_keyboard


class UserService:

    def __init__(self, api_context: APIOptionsRequestContext):
        self.api_context = api_context

    async def greet_user(self, event: SimpleBotEvent, user: User):
        user_data = (await self.api_context.users.get(user_ids=event.object.object.message.from_id)).response[0]
        await event.answer(messages.HELLO_MESSAGE.format(user_data.first_name),
                           keyboard=main_keyboard.get_keyboard())
