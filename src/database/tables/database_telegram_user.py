from typing import Self, Optional

from src.database import Database
from src.database.models.telegram_user_model import TelegramUserModel
from src.database.utils import log_debug

_table_name = "telegram_user"


class DatabaseTelegramUser:
    def __init__(self, database: Database, telegram_id: int):
        self.__telegram_id: int = telegram_id
        self.__database = database
        self.__conn = self.__database.get_connect

    async def get_user_data(self) -> Optional[TelegramUserModel]:
        if self.__telegram_id is None:
            raise ValueError("Telegram ID is None")
        result = await self.__conn.fetchrow(f"SELECT * FROM {_table_name} WHERE id = $1",
                                            self.__telegram_id)
        if not result:
            return None
        log_debug(f"[DB TELEGRAM USER] | Received user data with telegram_id={self.__telegram_id}")

        return TelegramUserModel(**result)

    @classmethod
    async def init_user_with_create(cls, database: Database, telegram_id: int, first_name: str,
                                    last_name: Optional[str] = None,
                                    username: Optional[str] = None,
                                    language_code: Optional[str] = None, is_premium: Optional[bool] = None,
                                    added_to_attachment_menu: Optional[bool] = None) -> Optional[Self]:
        conn = database.get_connect
        result = await conn.execute(f"INSERT INTO {_table_name} ("
                                    "id, "
                                    "first_name,"
                                    "last_name,"
                                    "username,"
                                    "language_code,"
                                    "is_premium,"
                                    "added_to_attachment_menu"
                                    ") VALUES ($1, $2, $3, $4, $5, $6, $7)",
                                    telegram_id,
                                    first_name, last_name, username, language_code, is_premium,
                                    added_to_attachment_menu)
        if not result:
            return None
        log_debug(f"[DB TELEGRAM USER] | User with telegram_id={telegram_id} created")

        return cls(database, telegram_id)

    @classmethod
    async def init_user_from_id(cls, database: Database, telegram_id: int) -> Optional[Self]:
        conn = database.get_connect
        user_telegram_id = await conn.fetchval(f"SELECT id FROM {_table_name} WHERE id = $1",
                                               telegram_id)
        if not user_telegram_id:
            return None
        log_debug(f"[DB TELEGRAM USER] | User with telegram_id={telegram_id} found")

        return cls(database, user_telegram_id)
