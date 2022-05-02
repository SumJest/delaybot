import os
import typing
import json


class Queue:
    id: int
    peer_id: int
    msg_id: int
    owner_id: int
    name: str
    members: typing.List[int]

    def __init__(self, msg_id: int = 0, name: str = "", owner_id: int = 0, id: int = None,
                 peer_id: int = None):
        self.msg_id = msg_id
        self.name = name
        self.owner_id = owner_id
        self.members = []
        self.id = id
        self.peer_id = peer_id

    def __repr__(self):
        return f"Id: {self.id}, Name: {self.name}, Owner: {self.owner_id}, " \
               f"Msg_id: {self.msg_id}, Count: {len(self.members)}, Peer_id: {self.peer_id}"

    def add_member(self, user_id: int):
        self.members.append(user_id)

    def remove_member(self, user_id: int):
        self.members.remove(user_id)

