from typing import Self, Optional

from src.database import Database
from src.database.models.app_user_model import AppUserModel
from src.database.utils import log_debug

_table_name = "app_user"


class DatabaseAppUser:
    def __init__(self, database: Database, user_id: int):
        self.__user_id: int = user_id
        self.__database = database
        self.__conn = self.__database.get_connect

    @property
    def user_id(self) -> int:
        return self.__user_id

    @classmethod
    async def init_user_with_create(cls, database: Database, telegram_id: Optional[int] = None) -> Optional[Self]:
        conn = database.get_connect
        user_id: int = await conn.fetchval(f"INSERT INTO {_table_name} (telegram_id) VALUES ($1) RETURNING id",
                                           telegram_id)
        if not user_id:
            return None

        log_debug(f"[DB APP USER] | User with telegram_id={telegram_id} created")
        return cls(database, user_id)

    @classmethod
    async def init_user_from_telegram_id(cls, database: Database, telegram_id: int) -> Optional[Self]:
        conn = database.get_connect
        user_app_id = await conn.fetchval(f"SELECT id FROM {_table_name} WHERE telegram_id = $1",
                                          telegram_id)
        if not user_app_id:
            return None
        log_debug(f"[DB APP USER] | User with telegram_id={telegram_id} found")
        return cls(database, user_app_id)

    async def get_user_data(self) -> Optional[AppUserModel]:
        result = await self.__conn.fetchrow(f"SELECT * FROM {_table_name} WHERE id = $1",
                                            self.__user_id)
        if not result:
            return None
        log_debug(f"[DB APP USER] | Received user data with user_id={self.__user_id}")
        return AppUserModel(**result)

    async def set_age(self, age: Optional[int]) -> Self:
        """
        Устанавливает указанный возраст пользователю
        :param age:
        :return:
        """
        await self.__conn.execute(f"UPDATE {_table_name} SET age = $1 WHERE id = $2", age, self.__user_id)
        log_debug(f"[DB APP USER] | Set age for user_id={self.__user_id}")
        return self
