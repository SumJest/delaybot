from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import connection
from database.exceptions import ObjectNotFoundError
from database.models import Queue


class QueueService:
    @classmethod
    @connection
    async def add_member(cls, session: AsyncSession, queue_id: int, user_id: int, position: Optional[int] = None):
        """
        Adds a user to the given queue.
        :param queue_id: Queue id.
        :param user_id: User id.
        :param position: Position of the user.
        :return: Queue instance | position
        :raise: AlreadyInQueueError if user is already in
        """
        queue = await Queue.get(session=session, id=queue_id)
        if queue is None:
            raise ObjectNotFoundError(Queue, {'queue_id': queue_id})
        members = queue.members
        if user_id not in members:
            if position is not None and 0 <= position < len(members):
                members.insert(position, user_id)
            else:
                members.append(user_id)
            queue.members = members
            print(queue.members)
            await queue.save(session=session)
        return queue

    @classmethod
    @connection
    async def remove_member(cls, session: AsyncSession, queue_id: int, user_id: int):
        """
        Removes a user from the given queue.
        :param queue_id: Queue id.
        :param user_id: User id.
        :return: None
        :raise: NotInQueueError if user not in queue.
        """
        queue = await Queue.get(session=session, id=queue_id)
        if queue is None:
            raise ObjectNotFoundError(Queue, {'queue_id': queue_id})
        members = queue.members
        print(user_id, members)
        if user_id in members:
            members.remove(user_id)
            queue.members = members
            print(queue.members)
            await queue.save(session=session)
        return queue

    @classmethod
    @connection
    async def move_member(cls, session: AsyncSession, queue_id: int, user_id: int, position: int):
        """
        Moves the given user to the given position.
        :param queue_id: Queue id.
        :param user_id: User id.
        :param position: Position of the user.
        :return: None
        :raise: NotInQueueError if user not in queue.
        """
        queue = await Queue.get(session=session, id=queue_id)
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
            await queue.save(session=session)
        return queue

    @classmethod
    @connection
    async def clear_queue(cls, session: AsyncSession, queue_id: int) -> Queue:
        """
        Clears the given queue.
        :param queue_id: Queue id.
        :return: None
        """
        queue = await Queue.get(session=session, id=queue_id)
        if not queue:
            raise ObjectNotFoundError(Queue, {'queue_id': queue_id})
        queue.members = []
        await queue.save(session=session)
        return queue
