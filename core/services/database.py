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
                                            name_for_report TEXT,
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

    async def user_exists(self,
                          user_id: int
                          ) -> bool:
        """Проверка на существования пользователя в базе"""
        answer: Any = Iterable[Row]
        async with sl.connect(self.db_path) as db:
            cursor = await db.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
            answer = await cursor.fetchmany(1)

        return bool(len(answer))

    async def add_user(self,
                       user_id: int,
                       username: str,
                       name_for_report: str = None
                       ) -> Any:
        """Добавление пользователя в базу"""
        async with sl.connect(self.db_path) as db:
            await db.execute('''INSERT INTO users (user_id, username, name_for_report, is_mailing) 
                            VALUES (?, ?, ?, ?)''',
                             (user_id, username, name_for_report, 1))
            await db.commit()

    async def set_is_mailing(self,
                             user_id: int,
                             value: bool
                             ) -> Any:
        """Установка флага рассылки для пользователя"""
        async with sl.connect(self.db_path) as db:
            await db.execute('''UPDATE users SET is_mailing = ? WHERE user_id = ?''', (int(value), user_id))
            await db.commit()

    async def set_name_for_report(self,
                                  user_id: int,
                                  value: str
                                  ) -> Any:
        """Установка ФИО, отображаемое в отчете"""
        async with sl.connect(self.db_path) as db:
            await db.execute('''UPDATE users SET name_for_report = ? WHERE user_id = ?''', (value, user_id))
            await db.commit()

    async def del_user(self,
                       user_id: int
                       ) -> Any:
        """Удаление пользователя из базы"""
        async with sl.connect(self.db_path) as db:
            await db.execute('''DELETE FROM users WHERE user_id = ?''', (user_id,))
            await db.commit()

    async def get_all_users(self) -> Any:
        """Получение всех пользователей"""
        async with sl.connect(self.db_path) as db:
            cursor = await db.execute('''SELECT * FROM users''')
            users = await cursor.fetchall()
            return users

    async def get_mailing_users(self) -> Any:
        """Получение пользователей для рассылки"""
        async with sl.connect(self.db_path) as db:
            cursor = await db.execute('''SELECT * FROM users WHERE is_mailing = 1''')
            users = await cursor.fetchall()
            return users

    async def __get_status_id(self,
                              status_name: str
                              ) -> Any:
        """Получение id статуса по его названию"""
        async with sl.connect(self.db_path) as db:
            if status_name is not None:
                cursor = await db.execute('''SELECT status_id FROM status WHERE status_name = ?''', (status_name,))
                row = await cursor.fetchone()
                return row[0]
            else:
                return None

    async def add_journal_entry(self,
                                checking_time: str,
                                user_id: int,
                                is_check: bool = False,
                                status_name: str = None,
                                reason_not_work: str = None
                                ) -> Any:
        """Добавление записи в журнал"""
        status_id = await self.__get_status_id(status_name)
        async with sl.connect(self.db_path) as db:
            await db.execute('''INSERT INTO journal (is_check, status_id, reason_not_work, checking_time, user_id)
                            VALUES (?, ?, ?, ?, ?)''',
                             (int(is_check), status_id, reason_not_work, checking_time, user_id))
            await db.commit()

    async def change_journal_entry_by_date(self,
                                           user_id: int,
                                           checking_date: str,
                                           is_check: bool = False,
                                           status_name: str = None,
                                           reason_not_work: str = None
                                           ) -> Any:
        """Изменение записи в журнале по конкретного пользователя за конкретный день"""
        status_id = await self.__get_status_id(status_name)
        async with sl.connect(self.db_path) as db:
            await db.execute('''UPDATE journal SET is_check = ?, status_id = ?, reason_not_work = ?
                            WHERE user_id = ? AND checking_time LIKE ?''',
                             (int(is_check), status_id, reason_not_work, user_id, checking_date+'%'))
            await db.commit()

    async def del_journal_entry_by_date(self,
                                        user_id: int,
                                        checking_date: str
                                        ) -> Any:
        """Удаление записи из журнала для конкретного пользователя за конкретный день"""
        async with sl.connect(self.db_path) as db:
            await db.execute('''DELETE FROM journal WHERE user_id = ? AND checking_time LIKE ?''',
                             (user_id, checking_date+'%'))
            await db.commit()
