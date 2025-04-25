from typing import Annotated

from advanced_alchemy.extensions.fastapi import filters
from advanced_alchemy.filters import SearchFilter
from advanced_alchemy.service import OffsetPagination
from fastapi import APIRouter, Depends, HTTPException, Query

from api.auth.auth_dependency import auth_initdata_user
from api.dependencies import get_services
from api.filters.limit_offset import provide_limit_offset_pagination
from api.filters.user import UserFilter
from api.schemas.user import UserSchema
from containers import ServicesContainer
from database.models import User

router = APIRouter(tags=["user"])


@router.get("/", response_model=OffsetPagination[UserSchema])
async def list_user(filter_query: Annotated[UserFilter, Query()],
                    limit_offset: Annotated[filters.LimitOffset, Depends(provide_limit_offset_pagination)],
                    user: User = Depends(auth_initdata_user),
                    services_container: ServicesContainer = Depends(get_services)) -> OffsetPagination[
    UserSchema]:
    user_service = services_container.user_service
    filters_ = []
    if filter_query.id_:
        filters_.append(User.id == filter_query.id_)
    if filter_query.username:
        filters_.append(SearchFilter('username', filter_query.username, True))
    results, total = await user_service.list_and_count(*filters_, limit_offset)
    return user_service.to_schema(results, total, filters=[limit_offset])

@router.get("/{user_id}/", response_model=UserSchema)
async def retrieve_share_queue(user_id: int,
                           user: User = Depends(auth_initdata_user),
                           services_container: ServicesContainer = Depends(get_services)) -> User:
    user_ = await services_container.user_service.get_one_or_none(User.id == user_id)
    if not user_:
        raise HTTPException(status_code=404, detail="User not found")
    return user_
