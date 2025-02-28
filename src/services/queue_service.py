from typing import Optional

from database.dao import ChatDAO, UserDAO, QueueDAO
from database.models import Chat, User, Queue
from database.connection import async_session_maker

from services.exceptions.queue import QueueClosedError, AlreadyInQueueError, NotInQueueError


class QueueService:
    async def create_queue(self, name: str, chat: Chat, owner: User, ):
        """
        Creates a new queue with the given name and chat.
        :param name: Name of the queue.
        :param chat: Chat instance.
        :param owner: Owner instance.
        :return: Queue instance.
        """
        async with async_session_maker() as session:
            queue = Queue(
                name=name,
                chat_id=chat.id,
                owner_id=owner.id,
            )
            session.add(queue)
            await session.commit()
            await session.refresh(queue)
            return queue

    async def add_user_to_queue(self, queue: Queue, user: User, position: Optional[int] = None):
        """
        Adds a user to the given queue.
        :param queue: Queue instance.
        :param user: User instance.
        :param position: Position of the user.
        :return: Queue instance | position
        :raise: AlreadyInQueueError if user is already in
        """
        async with async_session_maker() as session:
            await session.refresh(queue)
            if user.id in queue.members:
                raise AlreadyInQueueError
            if position is None:
                position = len(queue.members)
            queue.members.insert(position, user.id)
            session.add(queue)
            await session.commit()
            await session.refresh(queue)
            return queue

    async def remove_user_from_queue(self, queue: Queue, user: User):
        """
        Removes a user from the given queue.
        :param queue: Queue instance.
        :param user: User instance.
        :return: None
        :raise: NotInQueueError if user not in queue.
        """
        async with async_session_maker() as session:
            await session.refresh(queue)
            try:
                queue.members.remove(user.id)
            except ValueError:
                raise NotInQueueError
            session.add(Queue)
            await session.commit()
            return queue

    async def clear_queue(self, queue: Queue):
        """
        Clears the given queue.
        :param queue: Queue instance.
        :return: None
        """
        async with async_session_maker() as session:
            await session.refresh(queue)
            queue.members.clear()
            session.add(queue)
            await session.commit()
            return queue

    async def delete_queue(self, queue: Queue):
        """
        Deletes the given queue.
        :param queue: Queue instance.
        :return: None
        """
        async with async_session_maker() as session:
            session.delete(queue)
            await session.commit()

    async def move_user(self, queue: Queue, user: User, position: Optional[int] = None):
        """
        Moves the given user to the given position.
        :param queue: Queue instance.
        :param user: User instance.
        :param position: Position of the user.
        :return: None
        :raise: NotInQueueError if user not in queue.
        """
        async with async_session_maker() as session:
            await session.refresh(queue)
            if position is None:
                position = len(queue.members)
            try:
                queue.members.remove(user.id)
            except ValueError:
                raise NotInQueueError
            queue.members.insert(position, user.id)
            session.add(queue)
            await session.commit()
            await session.refresh(queue)
            return queue
