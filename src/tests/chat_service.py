import unittest

from dependency_injector.wiring import inject, Provide

from models import User, Chat
from services import ChatService
from .container import ServicesContainer
from .database.test import with_test_db


class MockObject(object):
    pass


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
        event = MockObject()
        await self.chat_service.create_chat(event, user, chat)
        self.assertIsNotNone(chat.owner)
        self.assertEqual(chat.owner.user_id, user.user_id)
