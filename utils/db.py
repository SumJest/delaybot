import sqlite3
import typing

from utils import queue
from sqlite3 import Connection


class Database:
    sqlite_connection: Connection

    def __init__(self, path: str):
        self.sqlite_connection = sqlite3.connect(path)

    def get_first_free_id(self):
        cursor = self.sqlite_connection.cursor()
        sqlite_select_free_ids = '''
        SELECT id+1 as start_interval, next_id-1 as finish_interval
        FROM(
          SELECT id, LEAD(id)OVER(ORDER BY Id)as next_id
          FROM (
            SELECT 0 Id
            UNION ALL
            SELECT Id FROM queues
          )T
        )T
        WHERE id+1 <> next_id
        '''
        cursor.execute(sqlite_select_free_ids)
        results = cursor.fetchall()
        cursor.close()
        if not results:
            return None
        return results[0][0]

    def get_list(self, id: int):
        if id is None:
            return []
        cursor = self.sqlite_connection.cursor()
        cursor.execute(f"SELECT value FROM lists where id={id}")
        result = cursor.fetchall()
        lst = [e[0] for e in result]
        cursor.close()
        return lst

    def del_list(self, id: int):
        cursor = self.sqlite_connection.cursor()
        cursor.execute(f"delete from lists where id={id}")
        self.sqlite_connection.commit()
        cursor.close()

    def save_list(self, lst: list, id: int = None):
        cursor = self.sqlite_connection.cursor()
        __id = id
        if len(lst) == 0:
            return None
        if __id is None:
            cursor.execute("SELECT id FROM lists GROUP BY id")
            ids = sorted(e[0] for e in cursor.fetchall())

            __id = -1
            for i in range(len(ids)):
                if i != ids[i]:
                    __id = i
                    break
            if __id == -1:
                __id = len(ids)
        else:
            cursor.execute(f"DELETE from lists where id={__id}")
        for a in lst:
            cursor.execute(f"INSERT into lists VALUES ({__id}, {a});")
        self.sqlite_connection.commit()
        cursor.close()
        return __id

    def get_list_id(self, id: int):
        cursor = self.sqlite_connection.cursor()
        cursor.execute(f"SELECT list_id from queues where id={id}")
        list_id = cursor.fetchall()[0][0]
        cursor.close()
        return list_id

    def del_queue(self, id: int):
        cursor = self.sqlite_connection.cursor()
        list_id = self.get_list_id(id)
        cursor.execute(f"delete from queues where id={id}")
        if list_id is not None:
            cursor.execute(f"delete from lists where id={list_id}")
        cursor.close()
        self.sqlite_connection.commit()

    def get_queue(self, id: int):
        cursor = self.sqlite_connection.cursor()
        cursor.execute(f"SELECT * FROM queues WHERE id={id}")

        result = cursor.fetchall()
        if not result:
            return None
        q = queue.Queue(*result[0][3:], *result[0][:2])
        q.members = self.get_list(result[0][2])
        cursor.close()
        return q

    def get_queues(self, peer_id: int = None):
        cursor = self.sqlite_connection.cursor()
        if peer_id is not None:
            cursor.execute(f"SELECT * FROM queues WHERE peer_id={peer_id}")
        else:
            cursor.execute(f"SELECT * FROM queues")
        result = cursor.fetchall()
        if not result:
            return None
        queues: typing.List[queue.Queue] = []
        for tup in result:
            q = queue.Queue(*tup[3:], *tup[:2])
            q.members = self.get_list(tup[2])
            queues.append(q)
        cursor.close()
        return queues

    def get_ids_by_name(self, name: str, peer_id: int):
        cursor = self.sqlite_connection.cursor()
        cursor.execute(f"SELECT id FROM queues WHERE name='{name}' AND peer_id={peer_id}")
        result = cursor.fetchall()
        return [r[0] for r in result]

    def save_queue(self, q: queue.Queue):
        id = q.id
        list_id = None
        if id is not None:
            list_id = self.get_list_id(id)
            self.del_queue(id)

        list_id = self.save_list(q.members, list_id)
        cursor = self.sqlite_connection.cursor()
        if id is None:
            cursor.execute(f"INSERT into queues (peer_id, list_id, msg_id, name, owner_id) VALUES "
                           f"({q.peer_id},{'NULL' if list_id is None else list_id},{q.msg_id},'{q.name}',{q.owner_id});")
            cursor.execute("SELECT last_insert_rowid();")
            id = cursor.fetchall()[0][0]
        else:
            cursor.execute(f"INSERT into queues (id, peer_id, list_id, msg_id, name, owner_id) VALUES "
                           f"({id},{q.peer_id},{'NULL' if list_id is None else list_id},{q.msg_id},'{q.name}',"
                           f"{q.owner_id});")

        self.sqlite_connection.commit()

        cursor.close()
        return id

    def close(self):
        self.sqlite_connection.close()


def main():
    db = Database("C:\\Users\\Roman\\PycharmProjects\\delaybot\\queues.db")

    while True:
        # lst = list(map(int, input().split()))
        # if lst[0] == -1:
        #     break
        # id = db.save_list(lst)
        # print(id)
        # print(db.get_list(id))
        id = int(input())
        if id == -1:
            break
        print(db.get_list(id))

    db.close()


if __name__ == "__main__":
    main()
