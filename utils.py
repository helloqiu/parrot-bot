# -*- coding: utf-8 -*-
import sqlite3
import json
import random
import re

ONE_ARG_COMMAND_RE = re.compile(r'/(\S*)')
TWO_ARG_COMMAND_RE = re.compile(r'/(\S*)\s(\S*)')


def check_admin(group_id, user_id, bot):
    result = bot.get_group_member_info(group_id=group_id, user_id=user_id)
    if result['role'] in ['owner', 'admin']:
        return True
    else:
        return False


def lucky_enough(luck=0):
    """
    Check if you lucky enough.
    :param luck: should be an int between 0-100
    :return: Bool
    """
    return random.randint(0, 99) < luck


def compile_command(command):
    groups = TWO_ARG_COMMAND_RE.match(command)
    if groups:
        return groups.group(1), groups.group(2)
    else:
        groups = ONE_ARG_COMMAND_RE.match(command)
        if groups:
            return groups.group(1), None
        else:
            return None


__CREATE_TABLE_SQL__ = """
CREATE TABLE IF NOT EXISTS Parrot
(id TEXT PRIMARY KEY NOT NULL ,
value TEXT NOT NULL );
"""


class SQLiteStorage:

    def __init__(self, filename='parrot_session.sqlite3'):
        self.db = sqlite3.connect(filename, check_same_thread=False)
        self.db.text_factory = str
        self.db.execute(__CREATE_TABLE_SQL__)

    def __getitem__(self, id):
        return self.get(id)

    def __setitem__(self, id, session):
        self.set(id, session)

    def __delitem__(self, id):
        self.delete(id)

    def get(self, id):
        """
        根据 id 获取数据。
        :param id: 要获取的数据的 id
        :return: 返回取到的数据，如果是空则返回一个空的 ``dict`` 对象
        """
        session_json = self.db.execute(
            "SELECT value FROM Parrot WHERE id=? LIMIT 1;", (id,)
        ).fetchone()
        if session_json is None:
            return {}
        return json.loads(session_json[0])

    def set(self, id, value):
        """
        根据 id 写入数据。
        :param id: 要写入的 id
        :param value: 要写入的数据，可以是一个 ``dict`` 对象
        """
        self.db.execute(
            "INSERT OR REPLACE INTO Parrot (id, value) VALUES (?,?);",
            (id, json.dumps(value))
        )
        self.db.commit()

    def delete(self, id):
        """
        根据 id 删除数据。
        :param id: 要删除的数据的 id
        """
        self.db.execute("DELETE FROM Parrot WHERE id=?;", (id,))
        self.db.commit()
