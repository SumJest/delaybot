import asyncio
import json
import random
import re

from aiogram import Bot
from aiogram.types import Message, CallbackQuery

import settings
from keyboards.main import create_queue_keyboard
from keyboards.types import QueueAction
from keyboards.types.queue_action import QueueActionCallbackFactory
from models import Queue, User, Chat
from resources import messages


class QueueService:

    def __init__(self, bot: Bot):
        self.bot = bot


    def num_to_smiles(self, number: int):
        numbers = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
        smile_number = ''
        for a in str(number):
            smile_number += numbers[int(a)]
        return smile_number

    def represent_queue(self, queue: Queue):
        output = f"Очередь: {queue.name}\n"

        members = queue.members
        users = {user.user_id: user for user in User.select().where(User.user_id.in_(members))}

        for i, user in enumerate(queue.members):

            output += f"{self.num_to_smiles(i + 1)}. {users.get(user, None) or user}\n"
        output += f"\nСоздатель очереди: {queue.owner}"
        if queue.closed:
            output += "\n\n🚫 Закрыта для входа 🚫"
        return output

    async def update_queue_message(self, queue: Queue) -> bool:
        result = None
        if queue.msg_id:
            try:
                result = await self.bot.edit_message_text(
                    text=self.represent_queue(queue),
                    chat_id=queue.chat.peer_id,
                    message_id=queue.msg_id,
                    reply_markup=create_queue_keyboard(queue)
                )
            except:
                pass

        if result is None:
            response = await self.bot.send_message(chat_id=queue.chat.peer_id, text=self.represent_queue(queue),
                                                   reply_markup=create_queue_keyboard(queue))
            queue.msg_id = response.message_id
            queue.save()
            return True
        return False

    async def queue_list(self, event: Message, user: User, chat: Chat):
        queues = chat.queues
        if not queues.count():
            await event.answer("Очередей для этой беседы нет", reply_to_message_id=event.message_id)
            return
        else:
            for queue in queues:
                try:
                    await event.answer("очередь", reply_to_message_id=queue.msg_id)
                except Exception as ex:
                    await self.update_queue_message(queue)
                await asyncio.sleep(0.1)

    async def create_queue_event(self, queue_name, user: User, chat: Chat):
        if not queue_name:
            await self.bot.send_message(
                text=messages.ENTER_QUEUE_NAME,
                chat_id=chat.peer_id)
        queue = Queue.create(
            name=queue_name,
            chat=chat,
            msg_id=0,
            owner=user,
        )
        await self.update_queue_message(queue)

    async def queue_action_event(self,
                                 callback: CallbackQuery,
                                 callback_data: QueueActionCallbackFactory,
                                 user: User):
        queue: Queue = Queue.get_or_none(Queue.id == callback_data.queue_id)
        if queue is None:
            await callback.answer(text="Ошибка: очередь не найдена в базе ;-(!", show_alert=True)
            return
        chat = queue.chat
        match callback_data.action:
            case QueueAction.JOIN:
                if user.user_id in queue.members:
                    await callback.answer(text="Ты уже состоишь в очереди!", show_alert=True)
                else:
                    queue.members.append(user.user_id)
                    queue.save()
                    result = await self.update_queue_message(queue)
                    if result:
                        await callback.answer(text="Сообщение слишком старое, я отправил новое!", show_alert=True)

            case QueueAction.LEAVE:
                if user.user_id in queue.members:
                    queue.members.remove(user.user_id)
                    queue.save()
                    result = await self.update_queue_message(queue)
                    if result:
                        await callback.answer(text="Сообщение слишком старое, я отправил новое!", show_alert=True)

                else:
                    await callback.answer(text="Ты не состоишь в очереди!", show_alert=True)
            case QueueAction.CLEAR:
                if queue.owner == user or user.is_admin:
                    if not queue.members:
                        await callback.answer(text="Очередь пуста!", show_alert=True)
                        return
                    queue.members = []
                    queue.save()
                    result = await self.update_queue_message(queue)
                    if result:
                        await callback.answer(text="Сообщение слишком старое, я отправил новое!", show_alert=True)

                else:
                    await callback.answer(text="Только создатель может отчистить очередь!", show_alert=True)
            case QueueAction.DELETE:
                if queue.owner == user or user.is_admin:
                    queue.delete_instance()
                    try:
                        await self.bot.edit_message_text(chat_id=chat.peer_id,
                                                                  message_id=queue.msg_id,
                                                                  text=f"Очередь \"{queue.name}\" удалена!",
                                                                  reply_markup=None)
                    except:
                        await callback.answer(
                            text="Сообщение слишком старое, я не могу его отредактировать, но очередь удалена!",
                            show_alert=True)
                else:
                    await callback.answer(text="Только создатель может удалить очередь!", show_alert=True)
            case QueueAction.CLOSE | QueueAction.OPEN:
                if queue.owner == user or user.is_admin:
                    queue.closed = True if callback_data.action == QueueAction.CLOSE else False
                    queue.save()
                    await self.update_queue_message(queue)
                else:
                    await callback.answer(text="Только создатель может закрыть/открыть очередь!", show_alert=True)
