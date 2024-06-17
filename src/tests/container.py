
from containers import ServicesContainer
from .magic_mock import AsyncMock


test_services_container = ServicesContainer(api_context=AsyncMock(),
                                            fsm=AsyncMock())


test_services_container.wire(['tests.chat_service'])
print("WIRED")