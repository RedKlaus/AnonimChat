from typing import Optional, Coroutine, List

import asyncpg
from asyncpg import Connection

from src.config import ConnectDatabaseModel


async def database_is_exists(database_name: str, connect: Connection) -> bool:
    result = await connect.execute(
        f"""SELECT datname FROM pg_catalog.pg_database WHERE datname='{database_name}'""")
    return result == "SELECT 1"


async def table_is_exists(table_name: str, connect: Connection) -> bool:
    result = await connect.execute(
        f"""SELECT table_name FROM information_schema.tables WHERE table_name='{table_name}'""")
    return result == "SELECT 1"


class Database:
    def __init__(self, connect_database_model: ConnectDatabaseModel):
        self.__conn: Optional[Connection] = None
        self.__connect_database_model = connect_database_model

    @property
    def get_connect(self) -> Connection:
        if self.__conn is None:
            raise ConnectionError("Database connection is not initialized.")
        return self.__conn

    async def connect(self) -> Connection | None:
        if self.__conn is not None:
            await self.__conn.close()
        self.__conn = await asyncpg.connect(user=self.__connect_database_model.user,
                                            password=self.__connect_database_model.password,
                                            database=self.__connect_database_model.database,
                                            host=self.__connect_database_model.host,
                                            port=self.__connect_database_model.port)
        return self.__conn

    # Создание базы данных
    async def create_database(self) -> bool:
        connect = await asyncpg.connect(user=self.__connect_database_model.user,
                                        password=self.__connect_database_model.password,
                                        host=self.__connect_database_model.host,
                                        port=self.__connect_database_model.port)
        if await database_is_exists(self.__connect_database_model.database, connect):
            return False
        try:
            await connect.execute(f"""CREATE DATABASE {self.__connect_database_model.database}""")
        except asyncpg.exceptions.DuplicateDatabaseError:
            return False
        return True

    # Создание таблиц
    async def create_tables(self) -> List[str]:
        results: List[str] = []
        if not await table_is_exists("telegram_user", self.__conn):
            # telegram_user
            result = await self.__conn.execute("""CREATE TABLE telegram_user (
            id BIGINT PRIMARY KEY NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT,
            username TEXT,
            language_code TEXT,
            is_premium BOOLEAN,
            added_to_attachment_menu BOOLEAN
            )""")
            results.append(result)

        if not await table_is_exists("app_user", self.__conn):
            # app_user
            result = await self.__conn.execute("""CREATE TABLE app_user (
            id BIGSERIAL PRIMARY KEY NOT NULL,
            telegram_id BIGINT,
            age int,
            FOREIGN KEY (telegram_id) REFERENCES telegram_user(id) ON DELETE CASCADE ON UPDATE CASCADE
            )""")
            results.append(result)

        if not await table_is_exists("search_params", self.__conn):
            result = await self.__conn.execute("""CREATE TABLE search_params (
            user_id BIGINT PRIMARY KEY NOT NULL,
            interlocutor_age INT[] NOT NULL DEFAULT '{0, 100}',
            FOREIGN KEY (user_id) REFERENCES app_user(id) ON DELETE CASCADE ON UPDATE CASCADE
            )""")
            results.append(result)

        return results

    async def close(self) -> Coroutine:
        return await self.__conn.close()
