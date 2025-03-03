from typing import Optional

from database.connection import async_session_maker
from database.dao.base import BaseDAO
from database.models.queue import Queue


class QueueDAO(BaseDAO):
    model = Queue  # Определяем модель

    @classmethod
    async def add_member(cls, queue_id: int, user_id: int, position: int = None) -> Optional[Queue]:
        """Добавить пользователя в очередь."""
        async with async_session_maker() as session:
            queue = await cls.get(queue_id)
            if queue:
                members = queue.members
                if user_id not in members:
                    if position is not None and 0 <= position < len(members):
                        members.insert(position, user_id)
                    else:
                        members.append(user_id)
                    queue.members = members
                    await session.commit()
                    await session.refresh(queue)
            return queue

    @classmethod
    async def remove_member(cls, queue_id: int, user_id: int) -> Optional[Queue]:
        """Удалить пользователя из очереди."""
        async with async_session_maker() as session:
            queue = await cls.get(queue_id)
            if queue:
                members = queue.members
                if user_id in members:
                    members.remove(user_id)
                    queue.members = members
                    await session.commit()
                    await session.refresh(queue)
            return queue

    @classmethod
    async def move_member(cls, queue_id: int, user_id: int, new_position: int) -> Optional[Queue]:
        """Переместить пользователя в очереди."""
        async with async_session_maker() as session:
            queue = await cls.get(queue_id)
            if queue:
                members = queue.members
                if user_id in members:
                    members.remove(user_id)
                    if 0 <= new_position < len(members):
                        members.insert(new_position, user_id)
                    else:
                        members.append(user_id)
                    queue.members = members
                    await session.commit()
                    await session.refresh(queue)
            return queue
