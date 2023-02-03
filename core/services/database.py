from sqlite3 import Row, IntegrityError
from typing import Iterable, Any

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
        self.db_path = f'{Config.db_folder}chatbot.db'

    async def init_database(self):
        """Инициализация базы данных"""
        async with sl.connect(self.db_path) as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS users (
                                            user_id INTEGER PRIMARY KEY,
                                            username TEXT,
                                            name_for_report TEXT,
                                            is_mailing INTEGER,
                                            is_deleted INTEGER
                                            )''')

            await db.execute('''CREATE TABLE IF NOT EXISTS status (
                                            status_id INTEGER PRIMARY KEY,
                                            status_name TEXT,
                                            title TEXT
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
                await db.execute('''INSERT INTO status VALUES (1, "office","В офисе")''')
                await db.commit()
                await db.execute('''INSERT INTO status VALUES (2, "remote", "Удалённо")''')
                await db.commit()
                await db.execute('''INSERT INTO status VALUES (3, "not_work", "Не работаю")''')
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

    async def user_is_deleted(self,
                              user_id: int
                              ) -> bool:
        """Проверка на флаг удаленного пользователя"""
        answer: Any = Iterable[Row]
        async with sl.connect(self.db_path) as db:
            cursor = await db.execute('SELECT user_id FROM users WHERE user_id = ? AND is_deleted = 1', (user_id,))
            answer = await cursor.fetchmany(1)
        return bool(len(answer))

    async def user_is_mailing(self,
                              user_id: int
                              ) -> bool:
        """Проверка пользователя на флаг рассылки"""
        answer: Any = Iterable[Row]
        async with sl.connect(self.db_path) as db:
            cursor = await db.execute('SELECT user_id FROM users WHERE user_id = ? AND is_mailing = 1', (user_id,))
            answer = await cursor.fetchmany(1)
        return bool(len(answer))

    async def add_user(self,
                       user_id: int,
                       username: str,
                       name_for_report: str = None
                       ) -> Any:
        """Добавление пользователя в базу"""
        async with sl.connect(self.db_path) as db:
            await db.execute('''INSERT INTO users (user_id, username, name_for_report, is_mailing, is_deleted) 
                            VALUES (?, ?, ?, ?, ?)''',
                             (user_id, username, name_for_report, 1, 1))
            await db.commit()

    async def set_is_mailing(self,
                             user_id: int,
                             value: bool
                             ) -> Any:
        """Установка флага рассылки для пользователя"""
        async with sl.connect(self.db_path) as db:
            await db.execute('''UPDATE users SET is_mailing = ? WHERE user_id = ?''', (int(value), user_id))
            await db.commit()

    async def set_is_deleted(self,
                             user_id: int,
                             value: bool
                             ) -> Any:
        """Установка флага удаления для пользователя"""
        async with sl.connect(self.db_path) as db:
            await db.execute('''UPDATE users SET is_deleted = ? WHERE user_id = ?''', (int(value), user_id))
            await db.commit()

    async def set_name_for_report(self,
                                  user_id: int,
                                  value: str
                                  ) -> Any:
        """Установка ФИО, отображаемое в отчете"""
        async with sl.connect(self.db_path) as db:
            await db.execute('''UPDATE users SET name_for_report = ? WHERE user_id = ?''', (value, user_id))
            await db.commit()

    async def get_user_name_for_report(self,
                                       user_id: int
                                       ) -> str:
        """Получение имени для отчета пользователя"""
        async with sl.connect(self.db_path) as db:
            cursor = await db.execute('''SELECT name_for_report FROM users WHERE user_id = ?''', (user_id,))
            row = await cursor.fetchone()
            if row is not None:
                return row[0]
            else:
                return ''

    async def get_mailing_users(self) -> Any:
        """Получение пользователей для рассылки"""
        async with sl.connect(self.db_path) as db:
            cursor = await db.execute('''SELECT * FROM users WHERE is_mailing = 1 AND is_deleted = 0''')
            rows = await cursor.fetchall()
            return rows

    async def _get_status_id(self,
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

    async def _today_entry_exist(self,
                                 user_id,
                                 checking_time
                                 ) -> Any:
        """"""
        checking_date = checking_time.split(' ')[0]
        answer: Any = Iterable[Row]
        async with sl.connect(self.db_path) as db:
            cursor = await db.execute('SELECT journal_id FROM journal WHERE user_id = ? AND checking_time LIKE ?',
                                      (user_id, checking_date+'%'))
            answer = await cursor.fetchmany(1)
        return bool(len(answer))

    async def add_journal_entry(self,
                                checking_time: str,
                                user_id: int,
                                is_check: bool = False,
                                status_name: str = None,
                                reason_not_work: str = None,
                                message_id: int = None
                                ) -> Any:
        """Добавление записи в журнал"""
        status_id = await self._get_status_id(status_name)
        if await self._today_entry_exist(user_id, checking_time):
            checking_date = checking_time.split(' ')[0]
            async with sl.connect(self.db_path) as db:
                await db.execute('''UPDATE journal SET is_check = ?, status_id = ?, reason_not_work = ?
                                WHERE user_id = ? AND checking_time LIKE ?''',
                                 (int(is_check), status_id, reason_not_work, user_id, checking_date + '%'))
                await db.commit()
        else:
            async with sl.connect(self.db_path) as db:
                await db.execute('''INSERT INTO journal (is_check, status_id, reason_not_work, checking_time, user_id)
                                VALUES (?, ?, ?, ?, ?)''',
                                 (int(is_check), status_id, reason_not_work, checking_time, user_id))
                await db.commit()

    async def get_data_for_report(self,
                                  checking_date: str
                                  ) -> Any:
        """Получение данных для отчета"""
        async with sl.connect(self.db_path) as db:
            cursor = await db.execute('''SELECT 
                                            u.name_for_report, 
                                            CASE 
                                                WHEN j.is_check = TRUE THEN 'Отметился'
                                                WHEN j.is_check = FALSE THEN 'Не отметился'
                                            END AS is_check,
                                            s.title,
                                            j.reason_not_work, 
                                            date(j.checking_time) AS checking_date                         
                                        FROM journal j
                                        JOIN users u ON j.user_id = u.user_id
                                        LEFT JOIN status s ON j.status_id = s.status_id
                                        WHERE j.checking_time LIKE ?''', (checking_date+'%',))
            rows = await cursor.fetchall()
            return rows
