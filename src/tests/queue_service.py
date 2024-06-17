import unittest
from unittest.mock import MagicMock, AsyncMock

from dependency_injector.wiring import inject, Provide

from models import User, Chat, Queue
from services import QueueService
from .container import ServicesContainer
from .database.test import with_test_db


class QueueServiceTestCase(unittest.IsolatedAsyncioTestCase):
    @inject
    def setUp(self, queue_service: QueueService = Provide[ServicesContainer.queue_service]):
        self.queue_service = queue_service

    @with_test_db((Queue, User, Chat))
    async def test_represent_queue(self):
        chat = Chat.create(
            peer_id=123123
        )
        user = User.create(
            user_id=123123
        )
        queue = Queue.create(
            name="test",
            chat=chat,
            msg_id=0,
            owner=user,
        )
        user_data_mock_response = MagicMock()
        self.queue_service.api_context.users.get = AsyncMock(return_value=user_data_mock_response)

        result = await self.queue_service.represent_queue(queue)
        self.assertIsInstance(result, str)

    @with_test_db((Queue, User, Chat))
    async def test_update_queue_message_edit(self):
        chat = Chat.create(
            peer_id=123123
        )
        user = User.create(
            user_id=123123
        )
        queue = Queue.create(
            name="test",
            chat=chat,
            msg_id=1,
            owner=user,
        )

        self.queue_service.api_context.messages.send = AsyncMock()
        self.queue_service.api_context.messages.edit = AsyncMock()

        result = await self.queue_service.update_queue_message(queue)
        self.assertFalse(result)
        self.queue_service.api_context.messages.edit.assert_called()
        self.queue_service.api_context.messages.send.assert_not_called()

    @with_test_db((Queue, User, Chat))
    async def test_update_queue_message_send1(self):
        chat = Chat.create(
            peer_id=123123
        )
        user = User.create(
            user_id=123123
        )
        queue = Queue.create(
            name="test",
            chat=chat,
            msg_id=0,
            owner=user,
        )
        response = MagicMock()
        response.response[0].conversation_message_id = 123
        self.queue_service.api_context.messages.send = AsyncMock(return_value=response)
        self.queue_service.api_context.messages.edit = AsyncMock()
        result = await self.queue_service.update_queue_message(queue)
        self.assertTrue(result)
        self.queue_service.api_context.messages.edit.assert_not_called()
        self.queue_service.api_context.messages.send.assert_called()

        queue = Queue.get(
            id=queue.id
        )
        self.assertEqual(queue.msg_id, 123)

    @with_test_db((Queue, User, Chat))
    async def test_update_queue_message_send2(self):
        chat = Chat.create(
            peer_id=123123
        )
        user = User.create(
            user_id=123123
        )
        queue = Queue.create(
            name="test",
            chat=chat,
            msg_id=2,
            owner=user,
        )
        response = MagicMock()
        response.response[0].conversation_message_id = 321
        self.queue_service.api_context.messages.send = AsyncMock(return_value=response)
        self.queue_service.api_context.messages.edit = AsyncMock(return_value=None)
        result = await self.queue_service.update_queue_message(queue)
        self.assertTrue(result)
        self.queue_service.api_context.messages.edit.assert_called()
        self.queue_service.api_context.messages.send.assert_called()

        queue = Queue.get(
            id=queue.id
        )
        self.assertEqual(queue.msg_id, 321)
