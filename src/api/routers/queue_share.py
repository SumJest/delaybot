from typing import Annotated

from advanced_alchemy.extensions.fastapi import filters
from advanced_alchemy.filters import or_, and_
from advanced_alchemy.service import OffsetPagination
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from starlette import status
from starlette.responses import Response

from api.auth.auth_dependency import auth_initdata_user
from api.dependencies import get_services
from api.filters.limit_offset import provide_limit_offset_pagination
from api.schemas.queue import QueueShareSchema, CreateQueueShareSchema, ActivateQueueShareSchema
from containers import ServicesContainer
from database.models import User, Queue, QueuePermission, QueueShare

router = APIRouter(tags=["queue_share"])


@router.get("/", response_model=OffsetPagination[QueueShareSchema])
async def list_share_queue(limit_offset: Annotated[filters.LimitOffset, Depends(provide_limit_offset_pagination)],
                           queue_id: int = Query(),
                           user: User = Depends(auth_initdata_user),
                           services_container: ServicesContainer = Depends(get_services)) -> OffsetPagination[
    QueueShareSchema]:
    statement = select(Queue).join(Queue.permissions, isouter=True)
    user_filter = or_(Queue.owner_id == user.id,
                      Queue.members.contains(func.to_jsonb(user.id)),
                      QueuePermission.user_id == user.id)
    queue = await services_container.queue_service.get_one_or_none(Queue.id == queue_id, user_filter,
                                                                   statement=statement,
                                                                   uniquify=True)
    queue_share_service = services_container.queue_share_service
    if not queue:
        raise HTTPException(status_code=404, detail="Queue not found")
    queue_share_filter = QueueShare.queue_id == queue_id
    if not await services_container.queue_service.can_manage(queue.id, user.id):
        queue_share_filter = and_(queue_share_filter, QueueShare.can_manage == False)

    results, total = await queue_share_service.list_and_count(queue_share_filter, limit_offset)
    return queue_share_service.to_schema(results, total, filters=[limit_offset])


@router.get("/{share_id}/", response_model=QueueShareSchema)
async def retrieve_share_queue(share_id: int,
                               user: User = Depends(auth_initdata_user),
                               services_container: ServicesContainer = Depends(get_services)) -> QueueShare:
    statement = select(QueueShare).join(QueueShare.queue).join(Queue.permissions, isouter=True)
    user_filter = or_(Queue.owner_id == user.id,
                      and_(QueuePermission.can_manage == True, QueuePermission.user_id == user.id))

    queue_share = await services_container.queue_share_service.get_one_or_none(QueueShare.id == share_id, user_filter,
                                                                               statement=statement,
                                                                               uniquify=True)
    if not queue_share or (not await services_container.queue_service.can_manage(queue_share.queue_id, user.id) and
                           queue_share.can_manage):
        raise HTTPException(status_code=404, detail="Queue share not found")

    queue_share_service = services_container.queue_share_service
    return queue_share_service.to_schema(queue_share)


@router.post("/", response_model=QueueShareSchema)
async def create_share_queue(queue_share_data: CreateQueueShareSchema,
                             user: User = Depends(auth_initdata_user),
                             services_container: ServicesContainer = Depends(get_services)):
    queue_id = queue_share_data.queue_id
    statement = select(Queue).join(Queue.permissions, isouter=True)
    user_filter = or_(Queue.owner_id == user.id,
                      and_(QueuePermission.can_manage == True, QueuePermission.user_id == user.id))
    queue = await services_container.queue_service.get_one_or_none(Queue.id == queue_id, user_filter,
                                                                   statement=statement,
                                                                   uniquify=True)
    if not queue:
        raise HTTPException(status_code=404, detail="Queue not found")

    queue_share = await services_container.queue_share_service.create_share(**queue_share_data.model_dump())
    return services_container.queue_share_service.to_schema(queue_share)


@router.delete("/{share_id}/")
async def destroy_share_queue(share_id: int,
                              user: User = Depends(auth_initdata_user),
                              services_container: ServicesContainer = Depends(get_services)):
    statement = select(QueueShare).join(QueueShare.queue).join(Queue.permissions, isouter=True)
    user_filter = or_(Queue.owner_id == user.id,
                      and_(QueuePermission.can_manage == True, QueuePermission.user_id == user.id))
    queue_share = await services_container.queue_share_service.get_one_or_none(QueueShare.id == share_id, user_filter,
                                                                               statement=statement,
                                                                               uniquify=True)
    if not queue_share:
        raise HTTPException(status_code=404, detail="Queue share not found")

    await services_container.queue_share_service.delete(share_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/activate/", response_model=QueueShareSchema)
async def activate_share_queue(queue_share_data: ActivateQueueShareSchema,
                               user: User = Depends(auth_initdata_user),
                               services_container: ServicesContainer = Depends(get_services)):
    queue_share = await services_container.queue_share_service.get_one_or_none(
        QueueShare.token == queue_share_data.token)
    if not queue_share:
        raise HTTPException(status_code=404, detail="Queue share not found")

    await services_container.queue_permission_service.grant_permission(queue_share.queue_id,
                                                                       user.id,
                                                                       queue_share.can_manage)
    await services_container.queue_share_service.delete(queue_share.id)
    sent = await services_container.bot_queue_service.notify_shared_user(user.id, queue_share.queue_id)
    data = services_container.queue_share_service.to_schema(queue_share, schema_type=QueueShareSchema)
    if not sent:
        payload = services_container.bot_queue_service.generate_queue_payload(queue_share.queue_id)
        data.start_link = services_container.bot_queue_service.generate_start_link(payload)
    return data
