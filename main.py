import asyncio
import json
import os
from datetime import datetime, timezone
import random
from typing import List

from vkwave.types.objects import MessagesMessageActionStatus, MessagesMessageAttachmentType, MessagesMessage

from utils import messages
from utils import Users
from utils import keyboard
from utils.Users import ActionStates, QueueMessage

from vkwave.bots import SimpleLongPollBot, SimpleBotEvent
from vkwave.api import API
from vkwave.client import AIOHTTPClient
from vkwave.bots.core.dispatching import filters
from threading import Thread

if not os.path.exists("users"):
    os.makedirs("users")
    print("\"users\" directory created...")
if not os.path.exists("logs"):
    os.makedirs("logs")
    print("\"logs\" directory created...")
if not os.path.exists("queue.txt"):
    open('queue.txt', 'w').close()
    print("'queue.txt' file created...")

# configurating tokens
if not os.path.exists("config.json"):
    print("You must have config.json file with your tokens...")
    file = open('config.json', 'w')
    file.write("{\n\tgroup_id: \"YOUR_GROUP_ID\",\n\t'\"vk_token\": \"YOUR_VK_BOT_TOKEN\"}")
    file.close()
    print("Token file created. Please past your tokens. Program will shutdown...")
    exit()
file = open('config.json', 'r')
config = json.loads(file.read())
file.close()

bot = SimpleLongPollBot(tokens=config["vk_token"], group_id=config["group_id"])

api_session = API(tokens=config['vk_token'], clients=AIOHTTPClient())
api = api_session.get_context()

can_types = ["photo", "video", "audio", "doc", "wall", "market", "poll"]

action_list: List[Users.User] = []

queue_messages: List[Users.QueueMessage] = []

print("Bot started!")
# ----------------------------

def get_random_id():
    return random.getrandbits(32)


def append_to_file(file_name, text):
    text_file = open(file_name, 'a', encoding='utf-8')
    text_file.write(text)
    text_file.close()


async def update_queue():
    lines: List[str] = []
    for msg in queue_messages:
        if msg.is_active:
            lines.append(json.dumps(msg.get_dict()) + "\n")
    queue_file = open('queue.txt', 'w')
    queue_file.writelines(lines)
    queue_file.close()


async def read_queue():
    queue_file = open('queue.txt', 'r')
    lines = queue_file.readlines()
    queue_file.close()
    for line in lines:
        try:
            dict_msg = json.loads(line.rstrip())
            queue_messages.append(QueueMessage(user_id=dict_msg["user_id"], chat=Users.Chat(dict_msg["chat"]["peer_id"],
                                                                                            dict_msg["chat"]["name"]),
                                               is_active=dict_msg["is_active"], time=dict_msg["time"],
                                               message=Users.Message(peer_id=dict_msg["message"]["peer_id"],
                                                                     message=dict_msg["message"]["message"],
                                                                     attachment=dict_msg["message"]["attachment"],
                                                                     random_id=dict_msg["message"]["random_id"],
                                                                     forward_messages=dict_msg["message"]["forward_messages"])))
        except:
            continue


def log(event):
    now = datetime.today()
    print(
        '[' + now.strftime("%d.%m.%Y-%H:%M:%S") + '] ' + ' (' + str(event.object.object.message.from_id) + '): ' + str(
            event.object.object.message.text))
    thread1 = Thread(target=append_to_file, args=(('logs/log ' + now.strftime("%d-%m-%Y" + '.txt')), (
            '[' + now.strftime("%d.%m.%Y-%H:%M:%S") + '] ' + ' (' + str(
        event.object.object.message.from_id) + '): ' + event.object.object.message.text + '\n'),))
    thread1.start()
    thread1.join()
    return


def get_random_id() -> int:
    return random.getrandbits(32)


@bot.message_handler(filters.TextFilter(["начать", "start"]), filters.MessageFromConversationTypeFilter("from_pm"))
async def start_message(event: SimpleBotEvent):
    log(event)
    if not Users.user_exists(event.object.object.message.from_id):
        user = Users.User(event.object.object.message.from_id)
        Users.update_user(user)
        user_data = (await event.api_ctx.users.get(user_ids=event.object.object.message.from_id)).response[0]
        await event.answer(str(messages.Messages.HELLO_MESSAGE).format(user_data.first_name),
                           keyboard=keyboard.main_keyboard.get_keyboard())


@bot.message_handler(filters.ChatActionFilter(MessagesMessageActionStatus.CHAT_INVITE_USER))
async def add_to_chat_event(event: SimpleBotEvent):
    if abs(event.object.object.message.action.member_id) == config["group_id"]:
        user_id = event.object.object.message.from_id
        user_data = (await event.api_ctx.users.get(user_ids=event.object.object.message.from_id)).response[0]

        if Users.user_exists(user_id):
            user = Users.get_user(user_id)
            if len(user.chats_list) < 5:
                user.chats_list.append(Users.Chat(event.object.object.message.peer_id))
                user.action_state = ActionStates.NAME_CHAT
                action_list.append(user)
                #Users.update_user(user)

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

@bot.message_handler(filters.TextStartswithFilter("удалить"))
async def text_message(event: SimpleBotEvent):
    log(event)
    if Users.user_exists(event.object.object.message.from_id):
        user = Users.get_user(event.object.object.message.from_id)
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
    log(event)
    if Users.user_exists(event.object.object.message.from_id):
        chats = ""
        user = Users.get_user(event.object.object.message.from_id)
        i = 1
        for chat in user.chats_list:
            chats += f"{i}. {chat.name}\n"
            i += 1
        if i == 1:
            return "У вас ещё нету бесед("

        return chats


@bot.message_handler(filters.TextFilter("очередь"), filters.MessageFromConversationTypeFilter("from_pm"))
async def chats_message(event: SimpleBotEvent):
    log(event)
    if Users.user_exists(event.object.object.message.from_id):
        user = Users.get_user(event.object.object.message.from_id)
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
    log(event)
    if Users.user_exists(event.object.object.message.from_id):
        is_founded = False
        for user in action_list:
            if event.object.object.message.from_id == user.user_id:
                is_founded = True
                action_list.remove(user)
                user.action_state = ActionStates.IDLE
                Users.update_user(user)
                await event.answer("Хорошо", keyboard=keyboard.main_keyboard.get_keyboard())
        if not is_founded:
            await event.answer("Хорошо", keyboard=keyboard.main_keyboard.get_keyboard())


@bot.message_handler(filters.TextFilter("запланировать"), filters.MessageFromConversationTypeFilter("from_pm"))
async def chats_message(event: SimpleBotEvent):
    log(event)
    if Users.user_exists(event.object.object.message.from_id):
        user = Users.get_user(event.object.object.message.from_id)
        if user.chats_list:
            user.action_state = ActionStates.QUEUE_UP_CHOOSE_CHAT
            action_list.append(user)
            await event.answer("Выберете беседу где нужно запланировать сообщение.",
                               keyboard=keyboard.create_chats_list_keyboard(user.chats_list).get_keyboard())
        else:
            await event.answer("У вас нету бесед.")
    else:
        return "Я вас не нашёл, пожалуйста напишите Начать"


@bot.message_handler(filters.MessageFromConversationTypeFilter("from_pm"))
async def text_message(event: SimpleBotEvent):
    log(event)
    print((await api.messages.get_by_id(message_ids=event.object.object.message.id)).response.items[0])
    for user in action_list:
        if event.object.object.message.from_id == user.user_id:
            if user.action_state == ActionStates.NAME_CHAT:
                action_list.remove(user)
                user.action_state = ActionStates.IDLE
                user.chats_list[len(user.chats_list) - 1].name = event.object.object.message.text
                Users.update_user(user)
                return f'Я успешно установил название "{event.object.object.message.text}" для последней беседы!'
            elif user.action_state == ActionStates.DELETE_CHAT:
                if event.object.object.message.payload is None:
                    return "Что-то пошло не так, нажмите отмена"
                payload = json.loads(event.object.object.message.payload)
                chat_id = int(payload["chat_id"])
                if len(user.chats_list) > chat_id:
                    action_list.remove(user)
                    chat = user.chats_list[chat_id]
                    user.chats_list.pop(chat_id)
                    user.action_state = ActionStates.IDLE
                    Users.update_user(user)
                    await event.answer(
                        f"Беседа \"{chat.name}\" удалена. Не забудьте исключить бота из этой беседы.",
                        keyboard=keyboard.main_keyboard.get_keyboard())
                else:
                    return "Данная беседа не найдена"
            elif user.action_state == ActionStates.QUEUE_UP_CHOOSE_CHAT:
                if event.object.object.message.payload is None:
                    return "Что-то пошло не так, нажмите отмена"
                payload = json.loads(event.object.object.message.payload)
                chat_id = int(payload["chat_id"])
                if len(user.chats_list) > chat_id:
                    action_list.remove(user)
                    user.action_state = ActionStates.QUEUE_UP_CHOOSE_TIME
                    action_list.append(user)
                    Users.update_user(user)
                    queue_messages.append(Users.QueueMessage(user.user_id, user.chats_list[chat_id]))
                    await event.answer("Выберете время сообщения по формату dd.mm.yyyy hh:MM",
                                       keyboard=keyboard.back_keyboard.get_keyboard())
            elif user.action_state == ActionStates.QUEUE_UP_CHOOSE_TIME:
                try:
                    qtime = datetime.strptime(event.object.object.message.text, "%d.%m.%Y %H:%M")
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
                            "Время установлено. Теперь введите сообщение, которое хотите отправить в будущем")
                    else:
                        action_list.remove(user)
                        user.action_state = ActionStates.IDLE
                        Users.update_user(user)
                        await event.answer("Произошла ошибка. Попробуйте начать всё заново",
                                           keyboard=keyboard.main_keyboard.get_keyboard())
                        await event.answer()
                except ValueError:
                    return "Неправильный формат времени, пример: 17.11.2021 12:30"
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
                    #forward = m.id
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
                        await update_queue()
                        await event.answer("Сообщение поставлено в очередь",
                                           keyboard=keyboard.main_keyboard.get_keyboard())
                else:
                    action_list.remove(user)
                    user.action_state = ActionStates.IDLE
                    Users.update_user(user)
                    await event.answer("Произошла ошибка. Попробуйте начать всё заново",
                                       keyboard=keyboard.main_keyboard.get_keyboard())


async def check_message():
    await read_queue()
    while True:
        await asyncio.sleep(0.33)
        now = datetime.now().timestamp()

        for m in queue_messages:
            if m.is_active and m.time <= now:
                queue_messages.remove(m)
                await update_queue()
                try:
                    print(await api.messages.send(peer_id=m.chat.peer_id, message=m.message.message,
                                                  attachment=m.message.attachment,
                                                  random_id=m.message.random_id,
                                                  forward_messages=m.message.forward_messages))
                except:
                    print("error")
                    await api.messages.send(peer_id=m.user_id, message="Ошибка при отправке вашего сообщения",
                                            random_id=get_random_id())


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(bot.run(True))
    loop.create_task(check_message())
    loop.run_forever()
