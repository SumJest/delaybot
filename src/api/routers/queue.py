import typing

from fastapi import APIRouter, Depends

from api.auth.auth_dependency import auth_initdata_user
from api.dependencies import get_services
from api.schemas.queue import QueueSchema
from containers import ServicesContainer
from database.models import User

router = APIRouter(tags=["queue"])


@router.get("/", response_model=typing.List[QueueSchema])
async def queue_list(user: User = Depends(auth_initdata_user),
                     services_container: ServicesContainer = Depends(get_services)):
    queue_service = services_container.queue_service
    results = await queue_service.list()
    return queue_service.to_schema(results)
