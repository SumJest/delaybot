from dependency_injector.wiring import inject, Provide
from sqlalchemy import event
from sqlalchemy.util import await_only

from bot.services import BotQueueService
from containers import ServicesContainer
from database.models import Queue


def sync_as_async(fn):
    def go(*arg, **kw):
        return await_only(fn(*arg, **kw))

    return go


@inject
async def queue_post_save(target, queue_service: BotQueueService = Provide[ServicesContainer.queue_service]):
    await queue_service.update_queue_message(target)


@inject
async def queue_post_delete(target, queue_service: BotQueueService = Provide[ServicesContainer.queue_service]):
    await queue_service.mark_deleted(target)


@event.listens_for(Queue, "after_insert")
@sync_as_async
async def queue_post_save_sync(mapper, connection, target):
    await queue_post_save(target)
    await target.save()


@event.listens_for(Queue, "before_update")
@sync_as_async
async def queue_post_save_sync(mapper, connection, target):
    print('event')
    await queue_post_save(target)


@event.listens_for(Queue, "before_delete")
@sync_as_async
async def queue_post_delete_sync(mapper, connection, target):
    await queue_post_delete(target)
