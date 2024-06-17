from unittest.mock import MagicMock

import smart_getenv
from vkwave.bots import SimpleLongPollBot


test_bot = SimpleLongPollBot(tokens=[smart_getenv.getenv("VK_TOKEN", type=str)],
                             group_id=smart_getenv.getenv("TEST_VK_GROUP_ID", type=int))


class MockApiContext:

    def __init__(self):
        self.send = MagicMock(return_value )

test_api_context = test_bot.api_context
