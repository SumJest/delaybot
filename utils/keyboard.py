from vkwave.bots import Keyboard, ButtonColor
from utils import Users
from typing import List

from utils.queue import Queue

main_keyboard = Keyboard(one_time=False, inline=False)
main_keyboard.add_text_button("Беседы", color=ButtonColor.PRIMARY)
main_keyboard.add_text_button("Очередь", color=ButtonColor.PRIMARY)
main_keyboard.add_row()
main_keyboard.add_text_button("Запланировать", color=ButtonColor.POSITIVE)
main_keyboard.add_row()
main_keyboard.add_text_button("Удалить", color=ButtonColor.POSITIVE)
main_keyboard.add_row()
main_keyboard.add_text_button("Редактировать", color=ButtonColor.POSITIVE)

back_keyboard = Keyboard(one_time=False, inline=False)
back_keyboard.add_text_button(text="Отмена", color=ButtonColor.NEGATIVE)

edit_keyboard = Keyboard(one_time=False, inline=False)
edit_keyboard.add_text_button("Беседу", color=ButtonColor.PRIMARY)
edit_keyboard.add_text_button("Сообщение", color=ButtonColor.PRIMARY)
edit_keyboard.add_row()
edit_keyboard.add_text_button(text="Отмена", color=ButtonColor.NEGATIVE)


def create_chats_list_keyboard(chats: List[Users.Chat]) -> Keyboard:
    chats_list_keyboard = Keyboard(one_time=False, inline=False)
    i = 0
    for chat in chats:
        chats_list_keyboard.add_text_button(text=chat.name, color=ButtonColor.PRIMARY, payload={'chat_id': i})
        chats_list_keyboard.add_row()
        i += 1
    chats_list_keyboard.add_text_button(text="Отмена", color=ButtonColor.NEGATIVE)
    return chats_list_keyboard


def create_chat_keyboard(chat_id: int, message_id: int) -> Keyboard:
    chat_keyboard = Keyboard(one_time=True, inline=True)
    chat_keyboard.add_text_button("Название", color=ButtonColor.POSITIVE, payload={'chat_id': chat_id,
                                                                                   'message_id': message_id})
    chat_keyboard.add_text_button("Удалить", color=ButtonColor.NEGATIVE, payload={'chat_id': chat_id,
                                                                                  'message_id': message_id})
    return chat_keyboard


def create_message_keyboard(m_id: int, message_id: int) -> Keyboard:
    msg_keyboard = Keyboard(one_time=True, inline=True)
    msg_keyboard.add_text_button("Отправить", color=ButtonColor.POSITIVE, payload={'m_id': m_id,
                                                                                   'message_id': message_id})
    msg_keyboard.add_text_button("Удалить", color=ButtonColor.NEGATIVE, payload={'m_id': m_id,
                                                                                 'message_id': message_id})
    return msg_keyboard


def create_cancel_keyboard(messsage_id: int) -> Keyboard:
    cancel_keyboard = Keyboard(one_time=False, inline=False)
    cancel_keyboard.add_text_button(text="Отмена", color=ButtonColor.NEGATIVE, payload={'message_id': messsage_id})
    return cancel_keyboard


def create_queue_keyboard(queue: Queue):
    queue_keyboard = Keyboard(inline=True)
    queue_keyboard.add_callback_button(text="Вступить", color=ButtonColor.POSITIVE, payload={'command': 'join',
                                                                                             'id': queue.id})
    queue_keyboard.add_callback_button(text="Покинуть", color=ButtonColor.NEGATIVE, payload={'command': 'leave',
                                                                                             'id': queue.id})
    queue_keyboard.add_row()
    queue_keyboard.add_callback_button(text="Очистить", color=ButtonColor.SECONDARY, payload={'command': 'clear',
                                                                                              'id': queue.id})
    queue_keyboard.add_callback_button(text="Удалить", color=ButtonColor.SECONDARY, payload={'command': 'delete',
                                                                                             'id': queue.id})
    return queue_keyboard

