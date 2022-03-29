import os
import typing
import json


class Queue:
    msg_id: int
    owner_id: int
    name: str
    members: typing.List[int]

    def __init__(self, msg_id: int = 0, name: str = "", owner_id: int = 0):
        self.msg_id = msg_id
        self.name = name
        self.owner_id = owner_id
        self.members = []

    def __repr__(self):
        return f"Name: {self.name}, Owner: {self.owner_id}, Msg_id: {self.msg_id}, Count: {len(self.members)}"

    def to_json(self):
        return json.dumps(self.__dict__)

    def add_member(self, user_id: int):
        self.members.append(user_id)

    def remove_member(self, user_id: int):
        self.members.remove(user_id)

    @staticmethod
    def from_json(queue_json: str):
        """
        Creates Queue object from json
        :param queue_json: json
        :return: Queue object
        """
        attr: dict = json.loads(queue_json)
        queue = Queue()

        for key in attr.keys():
            setattr(queue, key, attr[key])

        return queue


def get_queues_from_file(chat_id: int):
    queues: typing.List[Queue] = []
    if not os.path.exists(f"queues/{chat_id}.txt"):
        return queues
    with open(f"queues/{chat_id}.txt", 'r', encoding='utf8') as fd:
        for line in fd.readlines():
            queue = Queue.from_json(line)
            queues.append(queue)
        fd.close()
    return queues


def get_queue_from_file(chat_id: int, name: str):
    if not os.path.exists(f"queues/{chat_id}.txt"):
        return None
    with open(f"queues/{chat_id}.txt", 'r', encoding='utf8') as fd:
        for line in fd.readlines():
            queue = Queue.from_json(line)
            if queue.name == name:
                return queue
        fd.close()
    return None


def save_queues(chat_id: int, queues: typing.List[Queue]):
    with open(f"queues/{chat_id}.txt", 'w', encoding='utf8') as fd:
        fd.writelines([f"{queue.to_json()}\n" for queue in queues])
        fd.close()


def save_queue(chat_id: int, queue: Queue):
    queues = get_queues_from_file(chat_id)
    founded = False
    for i in range(len(queues)):
        if queues[i].name == queue.name:
            queues[i] = queue
            founded = True
            break
    if not founded:
        queues.append(queue)
    print(queues)
    save_queues(chat_id, queues)


def del_queue(chat_id: int, name: str):
    queues = get_queues_from_file(chat_id)
    for i in range(len(queues)):
        print(1, len(queues))
        if queues[i].name == name:
            queues.pop(i)
            break
    save_queues(chat_id, queues)
