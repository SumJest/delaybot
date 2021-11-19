import os
import json

from typing import List


class Chat(object):
    peer_id: int
    name: str

    def __init__(self, peer_id: int, name=None):
        if name is None:
            self.name = ""
        else:
            self.name = name
        self.peer_id = peer_id

    def __repr__(self):
        return f"peer_id: {self.peer_id}, name: {self.name}"

    def get_dict(self):
        return {'peer_id': self.peer_id, 'name': self.name}


class ActionStates(int):
    IDLE: int = 0
    NAME_CHAT: int = 1
    DELETE_CHAT: int = 2
    QUEUE_UP_CHOOSE_CHAT: int = 3
    QUEUE_UP_CHOOSE_TIME: int = 4
    QUEUE_UP_SEND_MESSAGE: int = 5
    EDIT_CHOOSE_WHAT: int = 6
    EDIT_CHOOSE_CHAT: int = 7
    EDIT_CHOOSE_MESSAGE: int = 8
    EDIT_CHAT_WHAT_TO_DO: int = 9
    EDIT_MESSAGE_WHAT_TO_DO: int = 10


class Message(object):
    peer_id: int
    message: str
    attachment: str
    forward_messages: str
    random_id: int

    def __init__(self, peer_id: int, random_id: int, message=None, attachment=None, forward_messages=None):
        self.peer_id = peer_id
        self.message = message
        self.attachment = attachment
        self.random_id = random_id
        self.forward_messages = forward_messages

    def get_dict(self) -> dict:
        msg = {'peer_id': self.peer_id, 'message': self.message, 'attachment': self.attachment,
               'random_id': self.random_id, 'forward_messages': self.forward_messages}
        return msg


class QueueMessage(object):
    message: Message
    time: float
    user_id: int
    chat: Chat
    is_active: bool

    def __init__(self, user_id: int, chat: Chat, is_active=False, time=None, message=None):
        self.user_id = user_id
        self.chat = chat
        self.time = time
        self.message = message
        self.is_active = is_active

    def get_dict(self) -> dict:
        msg = {'time': self.time, 'user_id': self.user_id, 'chat': self.chat.get_dict(), 'is_active': self.is_active,
               'message': self.message.get_dict()}
        return msg


class User(object):
    user_id: int
    chats_list: List[Chat]
    action_state: int

    def __init__(self, user_id: int, chats_list=None, action_state: int = 0):
        if chats_list is None:
            chats_list = []
        self.user_id = user_id
        self.chats_list = chats_list
        self.action_state = action_state

    def __repr__(self):
        return f"user_id: {self.user_id}, chat_list: {self.chats_list}, action_state: {self.action_state}"


def serialization(user: User) -> str:
    """
    Function serializing User object to json
    :param user: User object
    :return: Json string
    """
    chats_list = []
    for chat in user.chats_list:
        chats_list.append(json.dumps(chat.__dict__))
    user_dict = {"user_id": user.user_id, "chat_list": chats_list, "action_state": user.action_state}

    return json.dumps(user_dict)


def deserialization(user: str) -> User:
    """
    Function deserializing User object to json
    :param user: Json string
    :return: User object
    """
    user_dict = json.loads(user)
    chat_list = []
    for chat in user_dict["chat_list"]:
        chat_dict = json.loads(chat)
        chat_list.append(Chat(chat_dict["peer_id"], chat_dict["name"]))
    return User(user_id=user_dict["user_id"], chats_list=chat_list, action_state=user_dict["action_state"])


def read_users() -> List[User]:
    """
    Function reads directory users and got registered users
    :return: List of Users from file
    """
    users = []
    for file in os.listdir("users"):
        file = open("users/" + file, "r")
        users.append(deserialization(file.read()))
        file.close()
    return users


def get_user(user_id: int) -> User:
    """
    Function get user profile from file
    :param user_id:
    :return:
    """
    if f"{user_id}.txt" in os.listdir("users"):
        file = open(f"users/{user_id}.txt", "r")
        user = deserialization(file.read())
        file.close()
        return user
    else:
        print(f"File {user_id}.txt not found!")
        return User(user_id)


def user_exists(user_id: int) -> bool:
    """
    Function checks user profile in files
    :param user_id:
    :return: bool
    """
    return f"{user_id}.txt" in os.listdir("users")


def update_user(user: User):
    """
    Function update user file
    :param user:
    :return:
    """
    file = open("users/" + str(user.user_id) + ".txt", "w")
    file.write(serialization(user))
    file.close()
