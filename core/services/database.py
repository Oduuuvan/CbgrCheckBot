import datetime
from sqlite3 import Row, IntegrityError
from typing import Iterable, Any

import aiosqlite
import aiosqlite as sl
from core.config import Config


class DataBase:
    """База данных"""

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(DataBase, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        self.db_path = Config.db_path

    async def init_database(self):
        """Инициализация базы данных"""
        async with sl.connect(self.db_path) as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS users (
                                            user_id INTEGER PRIMARY KEY,
                                            username TEXT,
                                            first_name TEXT,
                                            last_name TEXT,
                                            is_mailing INTEGER
                                            )''')

            await db.execute('''CREATE TABLE IF NOT EXISTS status (
                                            status_id INTEGER PRIMARY KEY,
                                            status_name TEXT
                                            )''')

            await db.execute('''CREATE TABLE IF NOT EXISTS journal (
                                            journal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            is_check INTEGER,
                                            status_id INTEGER,
                                            reason_not_work TEXT,
                                            checking_time TEXT,
                                            user_id INTEGER,
                                            FOREIGN KEY(status_id) REFERENCES status(status_id),
                                            FOREIGN KEY(user_id) REFERENCES users(user_id)
                                            )''')

            try:
                await db.execute('''INSERT INTO status VALUES (1, "office")''')
                await db.commit()
                await db.execute('''INSERT INTO status VALUES (2, "remote")''')
                await db.commit()
                await db.execute('''INSERT INTO status VALUES (3, "not_work")''')
                await db.commit()
            except IntegrityError:
                pass

    async def user_exists(self, user_id: int) -> bool:
        """Проверка на существования пользователя в базе"""
        answer: Any = Iterable[Row]
        async with sl.connect(self.db_path) as db:
            cursor = await db.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
            answer = await cursor.fetchmany(1)

        return bool(len(answer))

    async def add_user(self, user_id: int, username: str, first_name: str, last_name: str):
        """Добавление пользователя в базу"""
        async with sl.connect(self.db_path) as db:
            await db.execute('''INSERT INTO users (user_id, username, first_name, last_name, is_mailing) 
                            VALUES (?, ?, ?, ?, ?)''',
                             (user_id, username, first_name, last_name, 1))
            await db.commit()

    async def del_user(self, user_id: int):
        async with sl.connect(self.db_path) as db:
            await db.execute('''DELETE FROM users WHERE user_id = ?''', (user_id,))
            await db.commit()

    async def set_is_mailing(self, user_id: int, value: int):
        """Установка флага рассылки для пользователя"""
        async with sl.connect(self.db_path) as db:
            await db.execute('''UPDATE users SET is_mailing = ? WHERE user_id = ?''', (value, user_id))
            await db.commit()

    async def add_journal_entry(self, is_check: bool, status_name: str, checking_time: str,
                                user_id: int,  reason_not_work: str = None):
        """Добавление записи в журнал"""
        async with sl.connect(self.db_path) as db:
            cursor = await db.execute('''SELECT status_id FROM status WHERE status_name = ?''', (status_name,))
            status_id = await cursor.fetchone()
            await db.execute('''INSERT INTO journal (is_check, status_id, reason_not_work, checking_time, user_id)
                            VALUES (?, ?, ?, ?, ?)''',
                             (int(is_check), status_id[0], reason_not_work, checking_time, user_id))
            await db.commit()

    async def del_journal_entry_by_date(self, user_id: int, date: str):
        """Удаление записи из журнала для конкретного пользователя за конкретный день"""
        async with sl.connect(self.db_path) as db:
            await db.execute('''DELETE FROM journal WHERE user_id = ? AND checking_time LIKE ?''',
                             (user_id, date+'%'))
            await db.commit()
