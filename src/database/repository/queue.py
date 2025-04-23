from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from database.models import Queue


class QueueRepository(SQLAlchemyAsyncRepository[Queue]):
    model_type = Queue
