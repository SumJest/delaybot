import asyncio
import json
import random
import re

from vkwave.api import APIOptionsRequestContext
from vkwave.api.methods._error import APIError
from vkwave.bots import SimpleBotEvent

import settings
from keyboards.main import create_queue_keyboard
from models import Queue, User, Chat


class QueueService:

    def __init__(self, api_context: APIOptionsRequestContext):
        self.api_context = api_context

    def get_random_id(self) -> int:
        return random.getrandbits(32)

    async def num_to_smiles(self, number: int):
        numbers = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
        smile_number = ''
        for a in str(number):
            smile_number += numbers[int(a)]
        return smile_number

    async def represent_queue(self, queue: Queue):
        output = f"Очередь: {queue.name}\n"
        sex = ['🐒', '🐱', '😺']

        members = queue.members

        for i in range(len(members)):
            user_data = (await self.api_context.users.get(user_ids=members[i], fields=['sex', ])).response[0]
            output += f"{self.num_to_smiles(i + 1)}. {user_data.first_name} {user_data.last_name} {sex[user_data.sex]}\n"
        owner_data = (await self.api_context.users.get(user_ids=queue.owner_id, fields=['sex', ])).response[0]
        output += f"\nСоздатель очереди: {owner_data.first_name} {owner_data.last_name} {sex[owner_data.sex]}"
        if queue.closed:
            output += "\n\n🚫 Закрыта для входа 🚫"
        return output

    async def update_queue_message(self, queue: Queue) -> bool:
        try:
            result = await self.api_context.messages.edit(peer_id=queue.chat, conversation_message_id=queue.msg_id,
                                                          message=(await self.represent_queue(queue)),
                                                          keyboard=create_queue_keyboard(queue).get_keyboard())
        except:
            result = None
        if result is not None:
            response = await self.api_context.messages.send(peer_ids=queue.chat, random_id=self.get_random_id(),
                                                            message=(await self.represent_queue(queue)),
                                                            keyboard=create_queue_keyboard(queue).get_keyboard())
            queue.msg_id = response.response[0].conversation_message_id
            queue.save()
            return True
        return False

    async def queue_list(self, event: SimpleBotEvent, user: User, chat: Chat):
        queues = chat.queues
        if not queues:
            await event.answer("Очередей для этой беседы нет", forward=json.dumps({
                'peer_id': chat.peer_id,
                'conversation_message_ids': [event.object.object.message.conversation_message_id],
                'is_reply': True
            }))
            return
        else:
            for queue in queues:
                try:
                    await event.answer("очередь", forward=json.dumps({
                        'peer_id': chat.peer_id,
                        'conversation_message_ids': queue.msg_id,
                        'is_reply': True
                    }))
                except APIError as ex:
                    await self.update_queue_message(queue)
                await asyncio.sleep(0.1)

    async def create_queue_event(self, event: SimpleBotEvent, user: User, chat: Chat):
        message = event.object.object.message.text
        message = message.replace(re.findall(f"\[club{settings.VK_GROUP_ID}\|[\S]+\]", message)[0], '')
        message = message.lstrip(', ')

        args = message.split(' ')
        queue_name = message[1:]

        queue = Queue.create(
            name=queue_name,
            chat=chat,
            msg_id=0,
            owner=user,
        )
        await self.update_queue_message(queue)

    async def queue_action_event(self, event: SimpleBotEvent, user: User):
        payload = event.object.object.payload
        chat_id = event.object.object.peer_id
        user_id = user.user_id
        queue_id = payload['id']
        queue: Queue = Queue.get_or_none(Queue.id == queue_id)
        if queue is None:
            await event.callback_answer(json.dumps({
                "type": "show_snackbar",
                "text": "Ошибка: очередь не найдена в базе ;-(!"
            }))
            return

        if payload['command'] == "join":
            if user_id in queue.members:
                await event.callback_answer(json.dumps({
                    "type": "show_snackbar",
                    "text": "Ты уже состоишь в очереди!"
                }))
                return
            else:
                queue.members.append(user_id)
                queue.save()
                result = await self.update_queue_message(queue)
                if result:
                    await event.callback_answer(json.dumps({
                        "type": "show_snackbar",
                        "text": "Сообщение слишком старое, я отправил новое!"
                    }))
                return
        elif payload['command'] == 'leave':
            if user_id in queue.members:
                queue.members.remove(user_id)
                queue.save()
                result = await self.update_queue_message(queue)
                if result:
                    await event.callback_answer(json.dumps({
                        "type": "show_snackbar",
                        "text": "Сообщение слишком старое, я отправил новое!"
                    }))
            else:
                await event.callback_answer(json.dumps({
                    "type": "show_snackbar",
                    "text": "Ты не состоишь в очереди!"
                }))
                return
        elif payload['command'] == 'clear':
            if queue.owner == user or user.is_admin:
                queue.members = []
                queue.save()
                result = await self.update_queue_message(queue)
                if result:
                    await event.callback_answer(json.dumps({
                        "type": "show_snackbar",
                        "text": "Сообщение слишком старое, я отправил новое!"
                    }))
            else:
                await event.callback_answer(json.dumps({
                    "type": "show_snackbar",
                    "text": "Только создатель может отчистить очередь!"
                }))
                return
        elif payload['command'] == 'delete':
            if queue.owner == user or user.is_admin:
                queue.delete()
                result = await self.api_context.messages.edit(peer_id=chat_id,
                                                              conversation_message_id=queue.msg_id,
                                                              message=f"Очередь \"{queue.name}\" удалена!",
                                                              keyboard="")
                if result is not None:
                    await event.callback_answer(json.dumps({
                        "type": "show_snackbar",
                        "text": "Сообщение слишком старое, я не могу его отредактировать, но очередь удалена!"
                    }))
            else:
                await event.callback_answer(json.dumps({
                    "type": "show_snackbar",
                    "text": "Только создатель может удалить очередь!"
                }))
                return
