import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional

from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from advanced_alchemy.filters import or_, and_
from sqlalchemy import select

from database.exceptions import ObjectNotFoundError
from database.models import Queue, QueuePermission, QueueShare
from database.repository.queue import QueueRepository, QueueShareRepository, QueuePermissionRepository


class QueueService(SQLAlchemyAsyncRepositoryService[Queue, QueueRepository]):
    repository_type = QueueRepository

    async def add_member(self, queue_id: int, user_id: int, position: Optional[int] = None):
        """
        Adds a user to the given queue.
        :param queue_id: Queue id.
        :param user_id: User id.
        :param position: Position of the user.
        :return: Queue instance | position
        :raise: AlreadyInQueueError if user is already in
        """
        queue = await self.get(queue_id)
        if queue is None:
            raise ObjectNotFoundError(Queue, {'queue_id': queue_id})
        members = queue.members
        if user_id not in members:
            if position is not None and 0 <= position < len(members):
                queue.members.insert(position, user_id)
            else:
                queue.members.append(user_id)
            queue = await self.update(queue, queue_id, auto_commit=True, auto_refresh=True)
        return queue

    async def remove_member(self, queue_id: int, user_id: int):
        """
        Removes a user from the given queue.
        :param queue_id: Queue id.
        :param user_id: User id.
        :return: None
        :raise: NotInQueueError if user not in queue.
        """
        queue = await self.get(queue_id)
        if queue is None:
            raise ObjectNotFoundError(Queue, {'queue_id': queue_id})
        members = queue.members
        if user_id in members:
            members.remove(user_id)
            queue.members = members
            await self.update(queue, queue_id, auto_commit=True)
        return queue

    async def move_member(self, queue_id: int, user_id: int, position: int):
        """
        Moves the given user to the given position.
        :param queue_id: Queue id.
        :param user_id: User id.
        :param position: Position of the user.
        :return: None
        :raise: NotInQueueError if user not in queue.
        """
        queue = await self.get(queue_id)
        if not queue:
            raise ObjectNotFoundError(Queue, {'queue_id': queue_id})
        members = queue.members
        if user_id in members:
            members.remove(user_id)
            if 0 <= position < len(members):
                members.insert(position, user_id)
            else:
                members.append(user_id)
            queue.members = members
            await self.update(queue, queue_id, auto_commit=True)
        return queue

    async def clear_queue(self, queue_id: int) -> Queue:
        """
        Clears the given queue.
        :param queue_id: Queue id.
        :return: None
        """
        queue = await self.get(queue_id)
        if not queue:
            raise ObjectNotFoundError(Queue, {'queue_id': queue_id})
        queue.members = []
        await self.update(queue, queue_id, auto_commit=True)
        return queue





class QueueShareService(SQLAlchemyAsyncRepositoryService[QueueShare, QueueShareRepository]):
    repository_type = QueueShareRepository

    async def create_share(self, queue_id: int, ttl: int = 3600, can_manage: bool = False) -> QueueShare:
        token = secrets.token_urlsafe(6)
        expires = datetime.now(timezone.utc) + timedelta(seconds=ttl)

        return await self.create({
            "queue_id": queue_id,
            "token": token,
            "expires_at": expires,
            "can_manage": can_manage,
        })

class QueuePermissionService(SQLAlchemyAsyncRepositoryService[QueuePermission]):
    repository_type = QueuePermissionRepository

    async def grant_permission(self, queue_id: int, user_id: int, can_manage=False) -> QueuePermission:
        perm = await self.get_one_or_none(QueuePermission.queue_id == queue_id,
                                          QueuePermission.user_id == user_id)
        if perm:
            perm.can_manage = perm.can_manage or can_manage
            return await self.update(perm)
        return await self.create({
            "queue_id": queue_id,
            "user_id": user_id,
            "can_manage": can_manage
        })
