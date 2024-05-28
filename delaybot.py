import asyncio
import traceback

from datetime import datetime
import random
from typing import List
import re
from vkwave.api.methods._error import APIError
from vkwave.types.objects import MessagesMessageActionStatus

import settings
from resources import messages
from utils import Users
from utils import keyboard
from utils import my_filters
from utils.db import Database
from utils.Users import ActionStates, QueueMessage

from vkwave.bots import SimpleLongPollBot, SimpleBotEvent
from vkwave.api import API
from vkwave.client import AIOHTTPClient
from vkwave.bots.core.dispatching import filters
from threading import Thread

from utils.queue import *


bot = SimpleLongPollBot(tokens=settings.VK_TOKEN, group_id=settings.VK_GROUP_ID)

api_session = API(tokens=settings.VK_TOKEN, clients=AIOHTTPClient())
api = api_session.get_context()

can_types = ["photo", "video", "audio", "doc", "wall", "market", "poll"]

action_list: List[Users.User] = []

queue_messages: List[Users.QueueMessage] = []

db = Database("queues.db")

print("Bot started!")


# ----------------------------


def get_random_id():
    return random.getrandbits(32)


def can_format(date_string: str, format: str) -> bool:
    try:
        datetime.strptime(date_string, format)
        return True
    except ValueError:
        pass
    return False


def append_to_file(file_name, text):
    text_file = open(file_name, 'a', encoding='utf-8')
    text_file.write(text)
    text_file.close()


async def edit_message(peer_id, conversation_message_id, message, keyboard):
    try:
        await api.messages.edit(peer_id=peer_id, conversation_message_id=conversation_message_id,
                                message=message,
                                keyboard=keyboard)
        return None
    except APIError as ex:
        return ex


async def update_queue():
    lines: List[str] = []
    for msg in queue_messages:
        if msg.is_active:
            lines.append(json.dumps(msg.get_dict()) + "\n")
    queue_file = open('queue.txt', 'w')
    queue_file.writelines(lines)
    queue_file.close()


# async def read_queue():
#     queue_file = open('queue.txt', 'r')
#     lines = queue_file.readlines()
#     queue_file.close()
#     for line in lines:
#         try:
#             dict_msg = json.loads(line.rstrip())
#             queue_messages.append(QueueMessage(user_id=dict_msg["user_id"], chat=Users.Chat(dict_msg["chat"]["peer_id"],
#                                                                                             dict_msg["chat"]["name"]),
#                                                is_active=dict_msg["is_active"], time=dict_msg["time"],
#                                                message=Users.Message(peer_id=dict_msg["message"]["peer_id"],
#                                                                      message=dict_msg["message"]["message"],
#                                                                      attachment=dict_msg["message"]["attachment"],
#                                                                      random_id=dict_msg["message"]["random_id"],
#                                                                      forward_messages=dict_msg["message"][
#                                                                          "forward_messages"])))
#         except:
#             continue


def get_random_id() -> int:
    return random.getrandbits(32)


async def queue_to_str(queue: Queue) -> str:
    output = f"Очередь: {queue.name}\n"

    for i in range(len(queue.members)):
        user_data = (await api.users.get(user_ids=queue.members[i])).response[0]
        output += f"{i + 1}. {user_data.first_name} {user_data.last_name}\n"
    owner_data = (await api.users.get(user_ids=queue.owner_id)).response[0]
    output += f"\nСоздатель: {owner_data.first_name} {owner_data.last_name}"
    return output


@bot.message_handler(filters.TextFilter("чаты"), filters.MessageFromConversationTypeFilter("from_pm"))
async def start_message(event: SimpleBotEvent):
    if Users.user_exists(event.object.object.message.from_id):
        user = Users.get_user(event.object.object.message.from_id)
        if user.user_id == 144268714:
            conversations_by_id = await api.messages.get_conversations_by_id(peer_ids=2000000002)
            conversations = await api.messages.get_conversations()
            print(conversations)
            print(conversations_by_id)


@bot.message_handler(filters.ChatActionFilter(MessagesMessageActionStatus.CHAT_INVITE_USER))
async def add_to_chat_event(event: SimpleBotEvent):
    if abs(event.object.object.message.action.member_id) == config["group_id"]:
        user_id = event.object.object.message.from_id
        user_data = (await event.api_ctx.users.get(user_ids=event.object.object.message.from_id)).response[0]

        if Users.user_exists(user_id):
            user = Users.get_user(user_id)
            if user.is_blocked:
                return "Вы заблокированы!"
            if len(user.chats_list) < 5:
                user.chats_list.append(Users.Chat(event.object.object.message.peer_id))
                user.action_state = ActionStates.NAME_CHAT
                action_list.append(user)
                # Users.update_user(user)

                await api.messages.send(user_id=user_id, random_id=get_random_id(),
                                        message="Вы только что добавили меня в "
                                                "беседу. Напишите мне, "
                                                "как вы хотите её назвать: ")
            else:
                await api.messages.send(user_id=user_id, random_id=get_random_id(),
                                        message="У вас достигнут лимит бесед! Я не добавил эту беседу.")
        else:
            await event.answer(f"[id{user_id}|{user_data.first_name}], ты не зарегистрирован у меня. Я не могу "
                               f"состоять в этой беседе! После регистрации, добавь меня ещё раз.")


# @bot.message_handler(filters.ChatActionFilter(MessagesMessageActionStatus.CHAT_KICK_USER))
# async def add_to_chat_event(event: SimpleBotEvent):
#     print("Увы(")
#     if abs(event.object.object.message.action.member_id) == config["group_id"]:
#         for user in Users.read_users():
#             for chat in user.chats_list:
#                 if chat.peer_id == event.object.object.message.peer_id:
#                     user.chats_list.remove(chat)
#                     api.messages.send(user_id=user.user_id, random_id=get_random_id(), message=f"К сожалению меня "
#                                                                                                f"кикнули из беседы "
#                                                                                              f"\"{chat.name}\". Приятно "
#                                                                                                f"было поработать!")
#                     Users.update_user(user)
#                     return None

@bot.message_handler(filters.TextStartswithFilter("удалить"), ~my_filters.payloadFilter())
async def del_message(event: SimpleBotEvent):
    if Users.user_exists(event.object.object.message.from_id):
        user = Users.get_user(event.object.object.message.from_id)
        if user.is_blocked:
            return "Вы заблокированы!"
        if user.chats_list:
            user.action_state = ActionStates.DELETE_CHAT
            action_list.append(user)
            await event.answer("Выберете беседу для удаления.",
                               keyboard=keyboard.create_chats_list_keyboard(user.chats_list).get_keyboard())
        else:
            await event.answer("У вас нету бесед.")
    else:
        return "Я вас не нашёл, пожалуйста напишите Начать"


@bot.message_handler(filters.TextFilter("беседы"), filters.MessageFromConversationTypeFilter("from_pm"))
async def chats_message(event: SimpleBotEvent):
    if Users.user_exists(event.object.object.message.from_id):
        chats = ""
        user = Users.get_user(event.object.object.message.from_id)
        if user.is_blocked:
            return "Вы заблокированы!"
        i = 1
        for chat in user.chats_list:
            chats += f"{i}. {chat.name}\n"
            i += 1
        if i == 1:
            return "У вас ещё нету бесед("

        return chats


@bot.message_handler(filters.TextFilter("очередь"), filters.MessageFromConversationTypeFilter("from_pm"))
async def chats_message(event: SimpleBotEvent):
    if Users.user_exists(event.object.object.message.from_id):
        user = Users.get_user(event.object.object.message.from_id)
        if user.is_blocked:
            return "Вы заблокированы"
        output = ""
        i = 1
        for qm in queue_messages:
            if qm.user_id == user.user_id and qm.is_active:
                output += f"{i}. В беседу: {qm.chat.name}. Дата: {datetime.fromtimestamp(qm.time).strftime('%d.%m.%Y %H:%M')}.\n"
                i += 1
        if i == 1:
            output = "У вас ещё нет запланированных сообщений"
        return output


@bot.message_handler(filters.TextFilter("отмена"), filters.MessageFromConversationTypeFilter("from_pm"))
async def chats_message(event: SimpleBotEvent):
    if Users.user_exists(event.object.object.message.from_id):
        if Users.get_user(event.object.object.message.from_id).is_blocked:
            return "Вы заблокированы!"
        for user in action_list:
            if event.object.object.message.from_id == user.user_id:
                action_list.remove(user)
                user.action_state = ActionStates.IDLE
                Users.update_user(user)
                break
        if event.object.object.message.payload is not None:
            message_id = json.loads(event.object.object.message.payload)['message_id']
            m = (await api.messages.get_by_id(message_ids=message_id)).response.items[0]
            attachments = ""
            for a in m.attachments:
                attach = json.loads(a.json())
                type = attach["type"]
                if type not in can_types:
                    await event.answer(f"Неподдерживаемый тип приложения \"{type}\". Исключаю его.")
                    continue
                if 'owner_id' not in attach[type].keys() or attach[type]['owner_id'] is None:
                    attach[type]['owner_id'] = attach[type]['from_id']
                attachments += f"{type}{attach[type]['owner_id']}_{attach[type]['id']}"
                if 'access_key' in attach[type].keys() and not attach[type]['access_key'] is None:
                    attachments += f"_{attach[type]['access_key']}"
                attachments += ","

            await api.messages.edit(peer_id=event.object.object.message.from_id, message=m.text,
                                    attachment=attachments,
                                    message_id=message_id)
        await event.answer("Отменил", keyboard=keyboard.main_keyboard.get_keyboard())




@bot.message_handler(filters.TextFilter("редактировать"), filters.MessageFromConversationTypeFilter("from_pm"))
async def chats_message(event: SimpleBotEvent):
    if Users.user_exists(event.object.object.message.from_id):
        user = Users.get_user(event.object.object.message.from_id)
        if user.is_blocked:
            return "Вы заблокированы!"
        user.action_state = ActionStates.EDIT_CHOOSE_WHAT
        action_list.append(user)
        await event.answer("Выберете что вы хотите отредактировать.",
                           keyboard=keyboard.edit_keyboard.get_keyboard())
    else:
        return "Я вас не нашёл, пожалуйста напишите Начать"


@bot.message_handler(filters.TextContainsFilter("очереди"), filters.MessageFromConversationTypeFilter("chat"))
async def chat_command_queues(event: SimpleBotEvent):
    chat_id = event.object.object.message.peer_id
    queues = db.get_queues(chat_id)
    if queues is None or len(queues) == 0:
        await event.answer("Очередей для этой беседы нет", forward=json.dumps({
            'peer_id': chat_id,
            'conversation_message_ids': [event.object.object.message.conversation_message_id],
            'is_reply': True
        }))
        return
    else:
        for queue in queues:
            try:
                await event.answer("очередь", forward=json.dumps({
                    'peer_id': chat_id,
                    'conversation_message_ids': queue.msg_id,
                    'is_reply': True
                }))
            except APIError as ex:
                response = await api.messages.send(peer_ids=chat_id, random_id=get_random_id(),
                                                   message=(await queue_to_str(queue)),
                                                   keyboard=keyboard.create_queue_keyboard(queue).get_keyboard())
                queue.msg_id = response.response[0].conversation_message_id
                await event.callback_answer(json.dumps({
                    "type": "show_snackbar",
                    "text": "Сообщение слишком старое, я отправил новое!"
                }))
                db.save_queue(queue)
            await asyncio.sleep(0.1)


@bot.message_handler(filters.TextContainsFilter("очередь"), filters.MessageFromConversationTypeFilter("chat"))
async def chat_command_queues(event: SimpleBotEvent):
    chat_id = event.object.object.message.peer_id
    try:
        message = event.object.object.message.text
        message = message.replace(re.findall(f"\[club{config['group_id']}\|[\S]+\]", message)[0], '')
        if message.lstrip(" ,").startswith("очередь") and message.replace("очередь", '').replace(' ', ''):
            message = message.replace("очередь", '').lstrip(" ,")
            name = message
            # if get_queue_from_file(chat_id, name) is not None:
            #     await event.answer(f"Очередь с имененем \"{name}\" уже существует", forward=json.dumps({
            #         'peer_id': chat_id,
            #         'conversation_message_ids': event.object.object.message.conversation_message_id
            #     }), disable_mentions=True)
            #     return
            queue = Queue(0, name, event.object.object.message.from_id, None, chat_id)
            response = await api.messages.send(peer_ids=[chat_id], message=(await queue_to_str(queue)),
                                               random_id=get_random_id())
            # print(response.response[0].conversation_message_id)
            queue.msg_id = response.response[0].conversation_message_id
            # save_queue(chat_id, queue)
            queue.id = db.save_queue(queue)
            await api.messages.edit(peer_id=chat_id, conversation_message_id=queue.msg_id,
                                    message=(await queue_to_str(queue)),
                                    keyboard=keyboard.create_queue_keyboard(queue).get_keyboard())
        else:
            await event.answer("Введите корректную команду!", forward=json.dumps({
                'peer_id': chat_id,
                'conversation_message_ids': event.object.object.message.conversation_message_id
            }))

    except:
        print(traceback.print_exc())
        return


@bot.message_handler(filters.MessageFromConversationTypeFilter("chat"))
async def chat_text_message(event: SimpleBotEvent):
    message = event.object.object.message.attachments[0].type

    try:
        message = event.object.object.message.text
        message = message.replace(re.findall(f"\[club{config['group_id']}\|[\S]+\]", message)[0], '')
        if Users.user_exists(event.object.object.message.from_id):
            user = Users.get_user(event.object.object.message.from_id)
            if user.action_state == ActionStates.IDLE:
                if user.is_blocked:
                    return "Вы заблокированы!"

                args = message.split()
                times = args[len(args) - 2]
                delay = args[len(args) - 1]
                user_data = (await event.api_ctx.users.get(user_ids=event.object.object.message.from_id)).response[0]
                if not str.isnumeric(times) or not str.isnumeric(delay):
                    return "Я не нашёл у тебя количество повторений и/или задержку"
                if int(times) > 15:
                    await event.answer(f"[id{user.user_id}|{user_data.first_name}], к сожалению я ограничен 15 "
                                       f"повторениями")
                    return
                if int(delay) > 30:
                    await event.answer(f"[id{user.user_id}|{user_data.first_name}], к сожалению я ограничен задержкой "
                                       f"в 30 секунд")
                    return
                await event.answer(f"[id{user.user_id}|{user_data.first_name}], исполняю {times} сообщений, раз "
                                   f"в {delay} секунд")
                await asyncio.sleep(1)
                for i in range(int(times)):
                    await event.answer(" ".join(args[:len(args) - 2]))
                    await asyncio.sleep(int(delay))
        else:
            return "Я вас не нашёл, пожалуйста напишите мне в личные сообщения Начать"
    except:
        return


@bot.message_handler(filters.MessageFromConversationTypeFilter("from_pm"))
async def text_message(event: SimpleBotEvent):
    for user in action_list:
        if event.object.object.message.from_id == user.user_id:
            if user.is_blocked:
                return "Вы заблокированы!"
            if user.action_state == ActionStates.NAME_CHAT:
                action_list.remove(user)
                user.action_state = ActionStates.IDLE
                user.chats_list[len(user.chats_list) - 1].name = event.object.object.message.text
                Users.update_user(user)
                await event.answer(f'Я успешно установил название "{event.object.object.message.text}" '
                                   f'для беседы!', keyboard=keyboard.main_keyboard.get_keyboard())
            elif user.action_state == ActionStates.DELETE_CHAT:
                if event.object.object.message.payload is None:
                    return "Что-то пошло не так, нажмите отмена"
                payload = json.loads(event.object.object.message.payload)
                chat_id = int(payload["chat_id"])
                if len(user.chats_list) > chat_id >= 0:
                    action_list.remove(user)
                    chat = user.chats_list[chat_id]
                    user.chats_list.pop(chat_id)
                    for qm in queue_messages:
                        if qm.chat.peer_id == chat.peer_id:
                            queue_messages.remove(qm)
                    await update_queue()
                    user.action_state = ActionStates.IDLE
                    Users.update_user(user)
                    await event.answer(
                        f"Беседа \"{chat.name}\" и запланированные сообщений в ней удалены. Не забудьте исключить бота "
                        f"из этой беседы.",
                        keyboard=keyboard.main_keyboard.get_keyboard())
                else:
                    return "Данная беседа не найдена"
            elif user.action_state == ActionStates.QUEUE_UP_CHOOSE_CHAT:
                if event.object.object.message.payload is None:
                    return "Что-то пошло не так, нажмите отмена"
                payload = json.loads(event.object.object.message.payload)
                chat_id = int(payload["chat_id"])
                if len(user.chats_list) > chat_id >= 0:
                    action_list.remove(user)
                    user.action_state = ActionStates.QUEUE_UP_CHOOSE_TIME
                    action_list.append(user)
                    Users.update_user(user)
                    queue_messages.append(Users.QueueMessage(user.user_id, user.chats_list[chat_id]))
                    await event.answer("Выберете время сообщения по формату 12:00 или 01.01.2001 12:00",
                                       keyboard=keyboard.back_keyboard.get_keyboard())
                else:
                    return "Что-то пошло не так, нажмите отмена"
            elif user.action_state == ActionStates.QUEUE_UP_CHOOSE_TIME:
                if can_format(event.object.object.message.text, "%d.%m.%Y %H:%M"):
                    qtime = datetime.strptime(event.object.object.message.text, "%d.%m.%Y %H:%M")
                elif can_format(event.object.object.message.text, "%H:%M"):
                    btime = datetime.strptime(event.object.object.message.text, "%H:%M")
                    now = datetime.now()
                    qtime = datetime.now()
                    qtime = qtime.replace(hour=btime.hour, minute=btime.minute)
                    if now.timestamp() > qtime.timestamp():
                        qtime = datetime.fromtimestamp(qtime.timestamp() + 86400)
                else:
                    return "Неправильный формат времени, пример: \"17.11.2021 12:30\" или \"12:30\""
                is_done = False
                for i in range(len(queue_messages) - 1, -1, -1):
                    if queue_messages[i].user_id == user.user_id and queue_messages[i].time is None:
                        queue_messages[i].time = qtime.timestamp()
                        is_done = True
                        break
                if is_done:
                    action_list.remove(user)
                    user.action_state = ActionStates.QUEUE_UP_SEND_MESSAGE
                    action_list.append(user)
                    await event.answer(
                        f"Время установлено на {qtime.strftime('%d.%m.%Y %H:%M')}. Теперь введите сообщение, которое "
                        f"хотите отправить в будущем")
                else:
                    action_list.remove(user)
                    user.action_state = ActionStates.IDLE
                    Users.update_user(user)
                    await event.answer("Произошла ошибка. Попробуйте начать всё заново",
                                       keyboard=keyboard.main_keyboard.get_keyboard())
                    await event.answer()
            elif user.action_state == ActionStates.QUEUE_UP_SEND_MESSAGE:
                is_found = False
                for i in range(len(queue_messages) - 1, -1, -1):
                    if queue_messages[i].user_id == user.user_id and queue_messages[i].message is None:
                        is_found = True
                        break
                if is_found:
                    m = (await api.messages.get_by_id(message_ids=event.object.object.message.id)).response.items[0]
                    attachments = ""
                    for a in m.attachments:
                        attach = json.loads(a.json())
                        type = attach["type"]
                        if type not in can_types:
                            await event.answer(f"Неподдерживаемый тип приложения \"{type}\". Исключаю его.")
                            continue
                        if 'owner_id' not in attach[type].keys() or attach[type]['owner_id'] is None:
                            attach[type]['owner_id'] = attach[type]['from_id']
                        attachments += f"{type}{attach[type]['owner_id']}_{attach[type]['id']}"
                        if 'access_key' in attach[type].keys() and not attach[type]['access_key'] is None:
                            attachments += f"_{attach[type]['access_key']}"
                        attachments += ","
                    # forward = m.id
                    # for m in m.fwd_messages:
                    #     forward += str(m.id) + ","
                    if not m.text and not attachments:
                        queue_messages.pop(i)
                        action_list.remove(user)
                        user.action_state = ActionStates.IDLE
                        Users.update_user(user)
                        await update_queue()
                        await event.answer("Пустое сообщение. Я не добавил его в очередь",
                                           keyboard=keyboard.main_keyboard.get_keyboard())
                    else:
                        queue_messages[i].message = Users.Message(queue_messages[i].chat.peer_id, get_random_id(),
                                                                  message=m.text, attachment=attachments)
                        queue_messages[i].is_active = True
                        action_list.remove(user)
                        user.action_state = ActionStates.IDLE
                        Users.update_user(user)
                        # queue_messages.sort(key=lambda qmes: qmes.time)
                        await update_queue()
                        await event.answer("Сообщение поставлено в очередь",
                                           keyboard=keyboard.main_keyboard.get_keyboard())
                else:
                    action_list.remove(user)
                    user.action_state = ActionStates.IDLE
                    Users.update_user(user)
                    await event.answer("Произошла ошибка. Попробуйте начать всё заново",
                                       keyboard=keyboard.main_keyboard.get_keyboard())
            elif user.action_state == ActionStates.EDIT_CHOOSE_WHAT:
                if event.object.object.message.text.lower() == "беседу":
                    if user.chats_list:
                        action_list.remove(user)
                        user.action_state = ActionStates.EDIT_CHOOSE_CHAT
                        action_list.append(user)
                        await event.answer("Выберете беседу для редактирования.",
                                           keyboard=keyboard.create_chats_list_keyboard(user.chats_list).get_keyboard())
                    else:
                        await event.answer("У вас нету бесед.")
                elif event.object.object.message.text.lower() == "сообщение":
                    output = ""
                    i = 1
                    for qm in queue_messages:
                        if qm.user_id == user.user_id and qm.is_active:
                            output += f"{i}. В беседу: {qm.chat.name}. Дата: {datetime.fromtimestamp(qm.time).strftime('%d.%m.%Y %H:%M')}.\n"
                            i += 1
                    if i == 1:
                        action_list.remove(user)
                        user.action_state = ActionStates.IDLE
                        Users.update_user(user)
                        await event.answer("У вас ещё нет запланированных сообщений",
                                           keyboard=keyboard.main_keyboard.get_keyboard())
                    else:
                        action_list.remove(user)
                        user.action_state = ActionStates.EDIT_CHOOSE_MESSAGE
                        action_list.append(user)
                        output = ""
                        i = 1
                        for qm in queue_messages:
                            if qm.user_id == user.user_id and qm.is_active:
                                output += f"{i}. В беседу: {qm.chat.name}. " \
                                          f"Дата: {datetime.fromtimestamp(qm.time).strftime('%d.%m.%Y %H:%M')}.\n"
                                i += 1
                        await event.answer(output)
                        await event.answer("Напишите номер сообщения для того, чтобы его просмотреть",
                                           keyboard=keyboard.back_keyboard.get_keyboard())
                else:
                    return "Выберете что вы хотите отредактировать сообщение или беседу"
            elif user.action_state == ActionStates.EDIT_CHOOSE_CHAT:
                if event.object.object.message.payload is None:
                    return "Что-то пошло не так, нажмите отмена"
                payload = json.loads(event.object.object.message.payload)
                chat_id = int(payload["chat_id"])
                if len(user.chats_list) > chat_id >= 0:
                    action_list.remove(user)
                    user.action_state = ActionStates.EDIT_CHAT_WHAT_TO_DO
                    action_list.append(user)

                    response = await api.messages.send(peer_id=user.user_id,
                                                       message=f"Беседа \"{user.chats_list[chat_id].name}\"",
                                                       random_id=get_random_id())
                    message_id = response.response
                    await event.answer("Выберете что хотите сделать с беседой",
                                       keyboard=keyboard.create_cancel_keyboard(message_id).get_keyboard())
                    await api.messages.edit(peer_id=user.user_id,
                                            message_id=message_id,
                                            message=f"Беседа \"{user.chats_list[chat_id].name}\"",
                                            keyboard=keyboard.create_chat_keyboard(chat_id, message_id).get_keyboard())
                else:
                    return "Данная беседа не найдена"
            elif user.action_state == ActionStates.EDIT_CHOOSE_MESSAGE:
                text = event.object.object.message.text
                if text.isdigit():
                    m_id = int(text)
                    queue_user_message: List[QueueMessage] = []
                    for qm in queue_messages:
                        if qm.user_id == user.user_id and qm.is_active:
                            queue_user_message.append(qm)
                    if len(queue_user_message) >= m_id > 0:
                        m = queue_user_message[m_id - 1]
                        action_list.remove(user)
                        user.action_state = ActionStates.EDIT_MESSAGE_WHAT_TO_DO
                        action_list.append(user)
                        response = await api.messages.send(peer_id=m.user_id, message=m.message.message,
                                                           attachment=m.message.attachment,
                                                           random_id=get_random_id(),
                                                           forward_messages=m.message.forward_messages)
                        message_id = response.response
                        await event.answer("Выберете что хотите сделать с сообщением",
                                           keyboard=keyboard.create_cancel_keyboard(message_id).get_keyboard())
                        await api.messages.edit(peer_id=m.user_id, message=m.message.message,
                                                attachment=m.message.attachment,
                                                message_id=message_id,
                                                keyboard=keyboard.create_message_keyboard(m_id,
                                                                                          message_id).get_keyboard())
                    else:
                        return "Сообщение с таким id не найдено"
                else:
                    return "Введите id сообщения"
            elif user.action_state == ActionStates.EDIT_MESSAGE_WHAT_TO_DO:
                if event.object.object.message.payload is None:
                    return "Что-то пошло не так, нажмите отмена"
                payload = json.loads(event.object.object.message.payload)
                m_id = int(payload["m_id"])
                message_id = int(payload["message_id"])
                queue_user_message: List[QueueMessage] = []
                for qm in queue_messages:
                    if qm.user_id == user.user_id and qm.is_active:
                        queue_user_message.append(qm)
                if m_id < 1 or m_id > len(queue_user_message):
                    return "Что-то пошло не так, нажмите отмена"
                text = event.object.object.message.text
                m = queue_user_message[m_id - 1]
                if text.lower() == "отправить":
                    queue_messages.remove(m)
                    await update_queue()
                    await api.messages.send(peer_id=m.chat.peer_id, message=m.message.message,
                                            attachment=m.message.attachment,
                                            random_id=m.message.random_id,
                                            forward_messages=m.message.forward_messages)
                    action_list.remove(user)
                    user.action_state = ActionStates.IDLE
                    Users.update_user(user)
                    await event.answer("Сообщение отправлено", keyboard=keyboard.main_keyboard.get_keyboard())
                elif text.lower() == "удалить":
                    queue_messages.remove(m)
                    await update_queue()
                    action_list.remove(user)
                    user.action_state = ActionStates.IDLE
                    Users.update_user(user)
                    await event.answer("Сообщение удалено из очереди", keyboard=keyboard.main_keyboard.get_keyboard())
                else:
                    return "Выберете что сделать с сообщением Отправить/Удалить"
                await api.messages.edit(peer_id=m.user_id, message=m.message.message,
                                        attachment=m.message.attachment,
                                        message_id=message_id)
            elif user.action_state == ActionStates.EDIT_CHAT_WHAT_TO_DO:
                if event.object.object.message.payload is None:
                    return "Что-то пошло не так, нажмите отмена"
                payload = json.loads(event.object.object.message.payload)
                chat_id = int(payload["chat_id"])
                message_id = int(payload["message_id"])
                if chat_id < 0 or chat_id >= len(user.chats_list):
                    return "Что-то пошло не так, нажмите отмена"
                text = event.object.object.message.text
                if text.lower() == "название":
                    action_list.remove(user)
                    user.action_state = ActionStates.NAME_CHAT
                    chat = user.chats_list.pop(chat_id)
                    user.chats_list.append(chat)
                    action_list.append(user)
                    await event.answer("Введите новое название:", keyboard.back_keyboard.get_keyboard())
                elif text.lower() == "удалить":
                    action_list.remove(user)
                    chat = user.chats_list.pop(chat_id)
                    for qm in queue_messages:
                        if qm.chat.peer_id == chat.peer_id:
                            queue_messages.remove(qm)
                    await update_queue()
                    user.action_state = ActionStates.IDLE
                    Users.update_user(user)
                    await event.answer(
                        f"Беседа \"{chat.name}\" и запланированные сообщений в ней удалены. Не забудьте исключить бота "
                        f"из этой беседы.",
                        keyboard=keyboard.main_keyboard.get_keyboard())
                else:
                    return "Выберете что сделать с беседой Название/Удалить"
                await api.messages.edit(peer_id=user.user_id,
                                        message_id=message_id,
                                        message=f"Беседа \"{user.chats_list[chat_id].name}\"")
            return


# async def check_message():
#     await read_queue()
#     while True:
#         await asyncio.sleep(0.33)
#         now = datetime.now().timestamp()
#
#         for m in queue_messages:
#             if m.is_active and m.time <= now:
#                 queue_messages.remove(m)
#                 await update_queue()
#                 try:
#                     print(await api.messages.send(peer_id=m.chat.peer_id, message=m.message.message,
#                                                   attachment=m.message.attachment,
#                                                   random_id=m.message.random_id,
#                                                   forward_messages=m.message.forward_messages))
#                 except:
#                     print("error")
#                     await api.messages.send(peer_id=m.user_id, message="Ошибка при отправке вашего сообщения",
#                                             random_id=get_random_id())


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(bot.run(True))
    # loop.create_task(check_message())
    loop.run_forever()
