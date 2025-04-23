from advanced_alchemy.filters import LimitOffset
from fastapi import Query


def provide_limit_offset_pagination(
        offset: int = Query(ge=0, default=0),
        limit: int = Query(ge=1, default=10, le=50),
) -> LimitOffset:
    return LimitOffset(limit, offset)
