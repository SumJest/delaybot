from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import connection
from database.models import User


class UserService:

    @classmethod
    @connection
    async def create_user(cls, session: AsyncSession, **kwargs):
        user = User(**kwargs)
        await user.save(session)
        return user
