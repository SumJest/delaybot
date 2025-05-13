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
from api.schemas.queue import QueueSchema, UpdateQueueSchema, DetailQueueSchema
from containers import ServicesContainer
from database.models import User, Queue, QueuePermission

router = APIRouter(tags=["queue"])


@router.get("/", response_model=OffsetPagination[QueueSchema])
async def list_queue(limit_offset: Annotated[filters.LimitOffset, Depends(provide_limit_offset_pagination)],
                     manage: bool | None = Query(None),
                     user: User = Depends(auth_initdata_user),
                     services_container: ServicesContainer = Depends(get_services)) -> OffsetPagination[QueueSchema]:
    queue_service = services_container.queue_service

    statement = select(Queue).distinct(Queue.id).join(Queue.permissions, isouter=True)
    user_filter = or_(Queue.owner_id == user.id,
                      Queue.members.contains(func.to_jsonb(user.id)),
                      QueuePermission.user_id == user.id)
    if manage:
        user_filter = and_(user_filter, or_(QueuePermission.can_manage == True,
                                            Queue.owner_id == user.id))
    results = await queue_service.list(user_filter, limit_offset,
                                       statement=statement)
    count_stmt = (
        select(func.count(func.distinct(Queue.id)))
        .select_from(Queue)
        .outerjoin(Queue.permissions)
        .where(user_filter)
    )
    total = (await services_container.queue_share_service.repository.session.execute(count_stmt)).scalar_one()
    return queue_service.to_schema(results, total, filters=[limit_offset])


@router.get("/{queue_id}/", response_model=DetailQueueSchema)
async def retrieve_queue(queue_id: int,
                         user: User = Depends(auth_initdata_user),
                         services_container: ServicesContainer = Depends(get_services)):
    statement = select(Queue).distinct(Queue.id).join(Queue.permissions, isouter=True)
    user_filter = or_(Queue.owner_id == user.id,
                      Queue.members.contains(func.to_jsonb(user.id)),
                      QueuePermission.user_id == user.id)
    queue = await services_container.queue_service.get_one_or_none(Queue.id == queue_id, user_filter,
                                                                   statement=statement)
    if not queue:
        raise HTTPException(status_code=404, detail="Queue not found")

    users = await services_container.user_service.list(User.id.in_(queue.members))
    users_dict = {user.id: user for user in users}
    queue_data = services_container.queue_service.to_schema(queue).to_dict()
    queue_data['members'] = [users_dict[user_id] for user_id in queue_data['members'] if user_id in users_dict]
    queue_data['can_manage'] = await services_container.queue_service.can_manage(queue.id, user.id)

    return queue_data


@router.patch("/{queue_id}/", response_model=QueueSchema)
async def partial_update_queue(queue_id: int,
                               queue_data: UpdateQueueSchema,
                               user: User = Depends(auth_initdata_user),
                               services_container: ServicesContainer = Depends(get_services)) -> Queue:
    statement = select(Queue).distinct(Queue.id).join(Queue.permissions, isouter=True)
    user_filter = or_(Queue.owner_id == user.id,
                      and_(QueuePermission.can_manage == True, QueuePermission.user_id == user.id))
    queue = await services_container.queue_service.get_one_or_none(Queue.id == queue_id, user_filter,
                                                                   statement=statement)
    if not queue:
        raise HTTPException(status_code=404, detail="Queue not found")

    to_update = queue_data.model_dump(exclude_unset=True)
    queue = await services_container.queue_service.update(to_update, queue_id)
    await services_container.bot_queue_service.update_queue_message(queue)
    return services_container.queue_service.to_schema(queue)


@router.delete("/{queue_id}/")
async def destroy_queue(queue_id: int,
                        user: User = Depends(auth_initdata_user),
                        services_container: ServicesContainer = Depends(get_services)):
    # TODO: Этот блок потом вынести в отдельный модуль прав
    statement = select(Queue).distinct(Queue.id).join(Queue.permissions, isouter=True)
    user_filter = or_(Queue.owner_id == user.id,
                      and_(QueuePermission.can_manage == True, QueuePermission.user_id == user.id))
    queue = await services_container.queue_service.get_one_or_none(Queue.id == queue_id, user_filter,
                                                                   statement=statement)
    if not queue:
        raise HTTPException(status_code=404, detail="Queue not found")
    # Конец блока
    await services_container.queue_service.delete(queue_id)
    await services_container.bot_queue_service.mark_deleted(queue)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
