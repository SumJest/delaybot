from aiogram.types import KeyboardButton, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from bot.keyboards.types.queue_action import QueueActionCallbackFactory, QueueAction
from bot.utils.helpers import encode_payload
from database.models import Queue
from settings import settings


def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="Беседы"),
        KeyboardButton(text="Очередь"),
    )
    builder.row(KeyboardButton(text="Запланировать"))
    builder.row(KeyboardButton(text="Удалить"))
    builder.row(KeyboardButton(text="Редактировать"))
    return builder.as_markup(resize_keyboard=True)


# def get_back_keyboard():
#     back_keyboard = Keyboard(one_time=False, inline=False)
#     back_keyboard.add_text_button(text="Отмена", color=ButtonColor.NEGATIVE)
#     return back_keyboard
#
#
# def get_edit_keyboard():
#     edit_keyboard = Keyboard(one_time=False, inline=False)
#     edit_keyboard.add_text_button("Беседу", color=ButtonColor.PRIMARY)
#     edit_keyboard.add_text_button("Сообщение", color=ButtonColor.PRIMARY)
#     edit_keyboard.add_row()
#     edit_keyboard.add_text_button(text="Отмена", color=ButtonColor.NEGATIVE)
#     return edit_keyboard
#
#
# def create_chats_list_keyboard(chats: List[Chat]) -> Keyboard:
#     chats_list_keyboard = Keyboard(one_time=False, inline=False)
#     for chat in chats:
#         chats_list_keyboard.add_text_button(text=chat.title,
#                                             color=ButtonColor.PRIMARY,
#                                             payload={'chat_id': chat.peer_id})
#         chats_list_keyboard.add_row()
#     chats_list_keyboard.add_text_button(text="Отмена", color=ButtonColor.NEGATIVE)
#     return chats_list_keyboard
#
#
# def create_chat_keyboard(chat: Chat, message_id: int) -> Keyboard:
#     chat_keyboard = Keyboard(one_time=True, inline=True)
#     chat_keyboard.add_text_button("Название", color=ButtonColor.POSITIVE, payload={'chat_id': chat.peer_id,
#                                                                                    'message_id': message_id})
#     chat_keyboard.add_text_button("Удалить", color=ButtonColor.NEGATIVE, payload={'chat_id': chat.peer_id,
#                                                                                   'message_id': message_id})
#     return chat_keyboard
#
#
# def create_message_keyboard(m_id: int, message_id: int) -> Keyboard:
#     msg_keyboard = Keyboard(one_time=True, inline=True)
#     msg_keyboard.add_text_button("Отправить", color=ButtonColor.POSITIVE, payload={'m_id': m_id,
#                                                                                    'message_id': message_id})
#     msg_keyboard.add_text_button("Удалить", color=ButtonColor.NEGATIVE, payload={'m_id': m_id,
#                                                                                  'message_id': message_id})
#     return msg_keyboard
#
#
# def create_cancel_keyboard(messsage_id: int) -> Keyboard:
#     cancel_keyboard = Keyboard(one_time=False, inline=False)
#     cancel_keyboard.add_text_button(text="Отмена", color=ButtonColor.NEGATIVE, payload={'message_id': messsage_id})
#     return cancel_keyboard

def create_queue_keyboard(queue: Queue):
    builder = InlineKeyboardBuilder()
    if queue.closed:
        builder.row(
            InlineKeyboardButton(
                text="Покинуть",
                callback_data=QueueActionCallbackFactory(
                    action=QueueAction.LEAVE,
                    queue_id=queue.id,
                ).pack()
            ),
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="Вступить",
                callback_data=QueueActionCallbackFactory(
                    action=QueueAction.JOIN,
                    queue_id=queue.id,
                ).pack()
            ),
            InlineKeyboardButton(
                text="Покинуть",
                callback_data=QueueActionCallbackFactory(
                    action=QueueAction.LEAVE,
                    queue_id=queue.id,
                ).pack()
            ),
        )

    # builder.row(
    #     InlineKeyboardButton(
    #         text="Очистить",
    #         callback_data=QueueActionCallbackFactory(
    #             action=QueueAction.CLEAR,
    #             queue_id=queue.id,
    #         ).pack()
    #     ),
    #     InlineKeyboardButton(
    #         text="Удалить",
    #         callback_data=QueueActionCallbackFactory(
    #             action=QueueAction.DELETE,
    #             queue_id=queue.id,
    #         ).pack()
    #     ),
    # )
    if queue.closed:
        builder.row(
            InlineKeyboardButton(
                text="Открыть",
                callback_data=QueueActionCallbackFactory(
                    action=QueueAction.OPEN,
                    queue_id=queue.id,
                ).pack()
            )
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="Закрыть",
                callback_data=QueueActionCallbackFactory(
                    action=QueueAction.CLOSE,
                    queue_id=queue.id,
                ).pack()
            )
        )

    builder.row(
        InlineKeyboardButton(
            text="Просмотр",
            url=f"https://t.me/queueeebot?startapp={encode_payload('queue', str(queue.id))}"
        )
    )
    return builder.as_markup()


async def build_queue_open_keyboard(queue_id: int) -> InlineKeyboardMarkup:
    """
    Строит клавиатуру с кнопкой открытия mini app очереди.
    """
    url = f"{settings.webapp_url}queue/{queue_id}"
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Открыть очередь",
            web_app=WebAppInfo(url=url)
        )
    )
    return builder.as_markup()

# def create_queue_keyboard(queue: Queue):
#     queue_keyboard = Keyboard(inline=True)
#     if not queue.closed:
#         queue_keyboard.add_callback_button(text="Вступить",
#                                            color=ButtonColor.POSITIVE,
#                                            payload={'command': QueueAction.JOIN,
#                                                     'id': queue.id})
#     queue_keyboard.add_callback_button(text="Покинуть",
#                                        color=ButtonColor.NEGATIVE,
#                                        payload={'command': QueueAction.LEAVE,
#                                                 'id': queue.id})
#     queue_keyboard.add_row()
#     queue_keyboard.add_callback_button(text="Очистить",
#                                        color=ButtonColor.SECONDARY,
#                                        payload={'command': QueueAction.CLEAR,
#                                                 'id': queue.id})
#     queue_keyboard.add_callback_button(text="Удалить",
#                                        color=ButtonColor.SECONDARY,
#                                        payload={'command': QueueAction.DELETE,
#                                                 'id': queue.id})
#     queue_keyboard.add_row()
#
#     if queue.closed:
#         queue_keyboard.add_callback_button(text="Открыть",
#                                            color=ButtonColor.SECONDARY,
#                                            payload={'command': QueueAction.OPEN,
#                                                     'id': queue.id})
#     else:
#         queue_keyboard.add_callback_button(text="Закрыть",
#                                            color=ButtonColor.SECONDARY,
#                                            payload={'command': QueueAction.CLOSE,
#                                                     'id': queue.id})
#     return queue_keyboard
