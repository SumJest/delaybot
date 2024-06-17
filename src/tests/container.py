
from containers import ServicesContainer
from unittest.mock import AsyncMock


test_services_container = ServicesContainer(api_context=AsyncMock(),
                                            fsm=AsyncMock())


test_services_container.wire(['tests.chat_service',
                              'tests.user_service',
                              'tests.queue_service'])
