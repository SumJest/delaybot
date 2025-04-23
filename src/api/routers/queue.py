from typing import Annotated

from advanced_alchemy.service import OffsetPagination
from fastapi import APIRouter, Depends

from api.auth.auth_dependency import auth_initdata_user
from api.dependencies import get_services
from api.filters.limit_offset import provide_limit_offset_pagination
from api.schemas.queue import QueueSchema
from containers import ServicesContainer
from database.models import User, Queue
from advanced_alchemy.extensions.fastapi import filters

router = APIRouter(tags=["queue"])


@router.get("/", response_model=OffsetPagination[QueueSchema])
async def queue_list(limit_offset: Annotated[filters.LimitOffset, Depends(provide_limit_offset_pagination)],
                     user: User = Depends(auth_initdata_user),
                     services_container: ServicesContainer = Depends(get_services)) -> OffsetPagination[QueueSchema]:
    queue_service = services_container.queue_service
    results, total = await queue_service.list_and_count(limit_offset, Queue.owner_id == user.id)
    return queue_service.to_schema(results, total, filters=[limit_offset])
