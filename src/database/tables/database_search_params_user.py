from typing import Self, List, Optional

from src.database import Database
from src.database.models.search_params_model import SearchParamsModel
from src.database.utils import log_debug

_table_name = "search_params"


class DatabaseSearchParamsUser:
    def __init__(self, database: Database, user_id: int):
        self.__user_id: int = user_id
        self.__database = database
        self.__conn = self.__database.get_connect

    @classmethod
    async def init_user(cls, database: Database, user_id: int) -> Optional[Self]:
        conn = database.get_connect
        result = await conn.fetchval(f"""SELECT user_id FROM {_table_name} WHERE user_id = $1""", user_id)
        if not result:
            return None
        log_debug(f"[DB SEARCH PARAMS] | User with user_id={user_id} found")
        return cls(database, user_id)

    @classmethod
    async def init_user_with_create(cls, database: Database, user_id: int,
                                    interlocutor_age: List[int]) -> Self:
        conn = database.get_connect
        await conn.execute(f"""INSERT INTO {_table_name} (user_id, interlocutor_age) VALUES ($1, $2)""", user_id,
                           interlocutor_age)
        log_debug(f"[DB SEARCH PARAMS] | Created search params for user_id={user_id}")
        return cls(database, user_id)

    async def get_search_params(self) -> Optional[SearchParamsModel]:
        result = await self.__conn.fetchrow(f"SELECT * FROM {_table_name} WHERE user_id = $1", self.__user_id)
        if not result:
            return None
        log_debug(f"[DB SEARCH PARAMS] | Received search params for user_id={self.__user_id}")
        return SearchParamsModel(**result)

    async def set_interlocutor_age(self, interlocutor_age: List[int]) -> Self:
        await self.__conn.execute(f"UPDATE {_table_name} SET interlocutor_age = $1 WHERE user_id = $2",
                                  interlocutor_age, self.__user_id)
        log_debug(f"[DB SEARCH PARAMS] | Set interlocutor age for user_id={self.__user_id}")
        return self
