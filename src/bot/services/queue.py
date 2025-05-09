import asyncio
import logging
import traceback

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramAPIError
from aiogram.types import Message, CallbackQuery

from bot.keyboards.main import create_queue_keyboard, build_queue_open_keyboard
from bot.keyboards.types import QueueAction
from bot.keyboards.types.queue_action import QueueActionCallbackFactory
from bot.utils.helpers import encode_payload
from database.models import Queue, User, Chat
from resources import messages
from services.chat_service import ChatService
from services.queue_service import QueueService
from services.user_service import UserService


class BotQueueService:

    def __init__(self, bot: Bot, queue_service: QueueService, user_service: UserService, chat_service: ChatService):
        self.bot = bot
        self.queue_service = queue_service
        self.user_service = user_service
        self.chat_service = chat_service

    def num_to_smiles(self, number: int):
        numbers = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
        smile_number = ''
        for a in str(number):
            smile_number += numbers[int(a)]
        return smile_number

    async def represent_queue(self, queue: Queue):
        output = f"📌 <b>Очередь</b>: <i>{queue.name}</i>\n"
        status_map = {
            True: "🔒 <b>Закрыта</b>\n",
            False: "🟢 <b>Открыта</b>\n",
        }
        output += status_map[queue.closed or False]
        members = queue.members or []
        result = await self.user_service.list(User.id.in_(members))
        users = {user.id: user for user in result}
        owner = await self.user_service.get(queue.owner_id)
        output += f"👤 <b>Создатель:</b> {owner}\n\n"
        output += "👥 <b>Участники:</b>\n"
        for i, user in enumerate(members):
            output += f"{self.num_to_smiles(i + 1)} {users.get(user, None) or user}\n"
        if not members:
            output += f"<i>Нет участников</i>"

        return output

    async def generate_queue_link(self, queue: Queue):
        return encode_payload('queue', str(queue.id))

    async def update_queue_message(self, queue: Queue) -> bool:
        result = None
        chat = await self.chat_service.get(queue.chat_id)
        if queue.msg_id:
            try:
                result = await self.bot.edit_message_text(
                    text=await self.represent_queue(queue=queue),
                    chat_id=chat.id,
                    message_id=queue.msg_id,
                    reply_markup=create_queue_keyboard(queue),
                    parse_mode='html'
                )

            except TelegramBadRequest as ex:
                if ex.message == ("Bad Request: message is not modified: specified new message content and reply "
                                  "markup are exactly the same as a current content and reply markup of the message"):
                    return True
                logging.info(traceback.format_exc())

        if result is None:
            response = await self.bot.send_message(chat_id=chat.id, text=await self.represent_queue(queue=queue),
                                                   reply_markup=create_queue_keyboard(queue), parse_mode='html')
            queue.msg_id = response.message_id
            await self.queue_service.update(queue, auto_commit=True)
            return True
        return False

    async def mark_deleted(self, queue: Queue):
        chat = await self.chat_service.get(queue.chat_id)
        owner = await self.user_service.get(queue.owner_id)
        try:
            await self.bot.edit_message_text(chat_id=chat.id,
                                             message_id=queue.msg_id,
                                             text=f"📌 <b>Очередь:</b> <i>{queue.name}</i>\n" \
                                                  f"⚠️ <b>Удалена</b>\n" \
                                                  f"👤 <b>Создатель:</b> {owner}",
                                             reply_markup=None,
                                             parse_mode='html')
        except TelegramBadRequest as ex:
            pass

    async def queue_list(self, event: Message, user: User, chat: Chat):
        queues = await self.queue_service.list(Queue.chat_id == (chat.id))
        if not queues:
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
                chat_id=chat.id)
            return
        queue = await self.queue_service.create(
            Queue(name=queue_name, owner_id=user.id, chat_id=chat.id),
            auto_commit=True
        )
        await self.update_queue_message(queue)

    async def queue_action_event(self,
                                 callback: CallbackQuery,
                                 callback_data: QueueActionCallbackFactory,
                                 user: User):
        queue: Queue = await self.queue_service.get_one_or_none(Queue.id == callback_data.queue_id)
        if queue is None:
            await callback.answer(text="Ошибка: очередь не найдена в базе ;-(!")
            return
        can_manage = await self.queue_service.can_manage(queue.id, user.id)
        match callback_data.action:
            case QueueAction.JOIN:
                if user.id in queue.members:
                    await callback.answer(text="Ты уже состоишь в очереди")
                    return
                queue = await self.queue_service.add_member(
                    queue_id=queue.id,
                    user_id=user.id,
                )
                await self.update_queue_message(queue)
            case QueueAction.LEAVE:
                if user.id not in queue.members:
                    await callback.answer(text="Тебя нет в очереди")
                    return
                queue = await self.queue_service.remove_member(
                    queue_id=queue.id,
                    user_id=user.id,
                )
                await self.update_queue_message(queue)
            case QueueAction.CLEAR:
                if can_manage or user.is_admin:
                    if not len(queue.members):
                        await callback.answer(text="Очередь пуста")
                        return
                    queue = await self.queue_service.clear_queue(
                        queue_id=queue.id,
                    )
                    await self.update_queue_message(queue)
                else:
                    await callback.answer(text="Только создатель может очистить очередь!")
            case QueueAction.DELETE:
                if can_manage or user.is_admin:
                    await self.queue_service.delete(queue.id, auto_commit=True)
                    await self.mark_deleted(queue)
                else:
                    await callback.answer(text="Только создатель может удалить очередь!")
            case QueueAction.CLOSE | QueueAction.OPEN:
                if can_manage or user.is_admin:
                    queue.closed = True if callback_data.action == QueueAction.CLOSE else False
                    queue = await self.queue_service.update(queue)
                    await self.update_queue_message(queue)
                else:
                    await callback.answer(text="Только создатель может закрыть/открыть очередь!")
        await callback.answer()

    async def notify_shared_user(self, user_id: int, queue_id: int) -> bool:
        """
        Отправляет пользователю уведомление о том, что ему поделились очередью.

        Возвращает True, если сообщение отправлено, False — иначе.
        Если пользователь до этого не начинал чат с ботом или заблокировал его,
        логируем и возвращаем False.

        :param user_id: Telegram user_id, которому поделились очередью
        :param queue_id: ID очереди
        :returns: bool - результат
        """
        # Получаем саму очередь
        queue = await self.queue_service.get(queue_id)
        # Проверяем, может ли пользователь управлять очередью
        can_manage = await self.queue_service.can_manage(queue_id, user_id)

        # Формируем права в читаемом виде
        rights = "Управление очередью" if can_manage else "Просмотр очереди"

        # Текст сообщения
        text = (
            f"📢 Вам предоставлен доступ к очереди «{queue.name}»\n\n"
            f"🔑 Ваши права: {rights}"
        )

        # Строим клавиатуру с кнопкой открытия мини-приложения
        keyboard = await build_queue_open_keyboard(queue_id)

        # Отправляем сообщение
        try:
            await self.bot.send_message(
                chat_id=user_id,
                text=text,
                reply_markup=keyboard
            )
        except TelegramAPIError as e:
            logging.warning(f"Ошибка Telegram API при отправке уведомления {user_id}: {e}")
            return False

        return True
