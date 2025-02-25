from aiogram import Bot
from aiogram.types import Message

from models import User
from resources import messages
from keyboards.main import get_main_keyboard


class UserService:

    def __init__(self, bot: Bot):
        self.bot = bot

    async def greet_user(self, event: Message, user: User):
        await event.answer(messages.HELLO_MESSAGE.format(event.from_user.first_name),
                           reply_markup=get_main_keyboard())
