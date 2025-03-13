import unittest
from unittest.mock import MagicMock

from dependency_injector.wiring import inject, Provide
from bot.middlewares.types.states import AddGroupStates
from database.models import User, Chat
from resources import messages
from bot.services import ChatService
from vkwave.bots import ForWhat

from .container import ServicesContainer
from .database.test import with_test_db


class ChatServiceTestCase(unittest.IsolatedAsyncioTestCase):
    @inject
    def setUp(self, chat_service: ChatService = Provide[ServicesContainer.chat_service]):
        self.chat_service = chat_service

    @with_test_db((User, Chat))
    async def test_create_chat(self):
        chat = Chat.create(
            peer_id=123123
        )
        user = User.create(
            user_id=123123
        )
        event = MagicMock()
        await self.chat_service.create_chat(event=event,
                                            user=user,
                                            chat=chat)
        self.chat_service.fsm.set_state.assert_called_once_with(event=event,
                                                                state=AddGroupStates.NAMING,
                                                                for_what=ForWhat.FOR_USER)
        self.chat_service.bot.messages.send.assert_called_once_with(
            user_id=user.user_id,
            message=messages.ADD_GROUP
        )
        self.assertIsNotNone(chat.owner)
        self.assertEqual(chat.owner.user_id, user.user_id)

    @with_test_db((User, Chat))
    async def test_name_chat(self):
        chat = Chat.create(
            peer_id=123456
        )
        user = User.create(
            user_id=123456
        )
        event = MagicMock()
        event.object.object.message.text = "Test chat name"
        await self.chat_service.name_chat(event=event,
                                          user=user,
                                          chat=chat)
        chat = Chat.get(peer_id=123456)
        self.chat_service.fsm.finish.assert_called_once_with(event=event,
                                                             for_what=ForWhat.FOR_USER)
        self.assertEqual(chat.name, "Test chat title")
