from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from database.models import Queue, QueueShare, QueuePermission


class QueueRepository(SQLAlchemyAsyncRepository[Queue]):
    model_type = Queue

class QueueShareRepository(SQLAlchemyAsyncRepository[QueueShare]):
    model_type = QueueShare

class QueuePermissionRepository(SQLAlchemyAsyncRepository[QueuePermission]):
    model_type = QueuePermission
