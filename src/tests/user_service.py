import unittest
from unittest.mock import MagicMock, AsyncMock

from dependency_injector.wiring import inject, Provide

from models import User, Chat
from services import UserService
from .container import ServicesContainer
from .database.test import with_test_db


class UserServiceTestCase(unittest.IsolatedAsyncioTestCase):
    @inject
    def setUp(self, user_service: UserService = Provide[ServicesContainer.user_service]):
        self.user_service = user_service

    @with_test_db((User, Chat))
    async def test_greet_user(self):
        user = User.create(
            user_id=123123
        )
        event = AsyncMock()
        user_data_mock_response = MagicMock()
        user_data_mock_response.response[0].first_name = "Roman"
        self.user_service.api_context.users.get = AsyncMock(return_value=user_data_mock_response)
        await self.user_service.greet_user(event=event, user=user)