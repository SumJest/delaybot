from vkwave.bots import Keyboard, ButtonColor
from utils import Users
from typing import List

main_keyboard = Keyboard(one_time=False, inline=False)
main_keyboard.add_text_button("Беседы", color=ButtonColor.PRIMARY)
main_keyboard.add_text_button("Очередь", color=ButtonColor.PRIMARY)
main_keyboard.add_row()
main_keyboard.add_text_button("Запланировать", color=ButtonColor.POSITIVE)
main_keyboard.add_row()
main_keyboard.add_text_button("Удалить", color=ButtonColor.POSITIVE)

back_keyboard = Keyboard(one_time=False, inline=False)
back_keyboard.add_text_button(text="Отмена", color=ButtonColor.NEGATIVE)


def create_chats_list_keyboard(chats: List[Users.Chat]) -> Keyboard:
    chats_list_keyboard = Keyboard(one_time=False, inline=False)
    i = 0
    for chat in chats:
        chats_list_keyboard.add_text_button(text=chat.name, color=ButtonColor.PRIMARY, payload={'chat_id': i})
        chats_list_keyboard.add_row()
        i += 1
    chats_list_keyboard.add_text_button(text="Отмена", color=ButtonColor.NEGATIVE)
    return chats_list_keyboard
