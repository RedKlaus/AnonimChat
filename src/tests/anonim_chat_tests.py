from typing import Optional, Coroutine

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from loguru import logger
from redis.asyncio import Redis
from redis.exceptions import ConnectionError

from src.config import ConnectDatabaseModel
from src.config.env_models import EnvConfigModel
from src.database import Database


class TestFunction:
    def __init__(self, func):
        self.__func = func

    def __str__(self) -> str:
        str_func = str(self.__func)
        return str_func.split(" ")[1]

    def __call__(self, *args, **kwargs):
        return self.__func(*args, **kwargs)

    def __await__(self, *args, **kwargs):
        return self.__func(*args, **kwargs)


def test_wrapper_async(_func):
    test_func = TestFunction(_func)

    async def wrapper(*args, **kwargs) -> bool:
        try:
            if bool(await test_func(*args, **kwargs)):
                logger.success(f"[{test_func}] - Test passed.")
                return True
        except Exception as _ex:
            logger.error(f"[{test_func}] - The test ended with an unknown error. | Ex: {_ex}")
        logger.warning(f"[{test_func}] - Test failed.")
        return False

    return wrapper


def test_wrapper(_func):
    test_func = TestFunction(_func)

    def wrapper(*args, **kwargs) -> bool:
        try:
            if bool(test_func(*args, **kwargs)):
                logger.success(f"[{test_func}] - Test passed.")
                return True
        except Exception as _ex:
            logger.error(f"[{test_func}] - The test ended with an unknown error. | Ex: {_ex}")
        logger.warning(f"[{test_func}] - Test failed.")
        return False

    return wrapper


class AnonimChatTests:
    def __init__(self, bot: Bot, connect_database_model: ConnectDatabaseModel, env_config_model: EnvConfigModel):
        self._bot = bot
        self._connect_database_model = connect_database_model
        self._env_config_model = env_config_model
        self._test_list = [
            self.test_check_environment,
            self.test_sub_channel,
            self.test_check_connect_redis,
            self.test_check_connect_postgresql,
        ]

    async def run_tests(self) -> bool:
        for i in self._test_list:
            call_func = i()
            if isinstance(call_func, Coroutine):
                result = await call_func
            else:
                result = call_func
            if not result:
                return False
        return True

    @test_wrapper_async
    async def test_sub_channel(self) -> Optional[bool]:
        try:
            return bool(await self._bot.get_chat(self._env_config_model.SUBSCRIBE_TELEGRAM_CHANNEL))
        except TelegramBadRequest as _ex:
            if _ex.message != "Bad Request: chat not found":
                raise _ex
            logger.warning(f"Bot couldn't find the channel, maybe he's not subscribed to the channel")

    @test_wrapper_async
    async def test_check_connect_redis(self) -> Optional[bool]:
        try:
            conn = Redis(host=self._env_config_model.REDIS_HOST, port=self._env_config_model.REDIS_PORT)
            await conn.ping()
            return True
        except ConnectionError:
            logger.warning("Failed to connect to redis")

    @test_wrapper_async
    async def test_check_connect_postgresql(self) -> Optional[bool]:
        database = Database(self._connect_database_model)
        try:
            return bool(await database.connect())
        except ConnectionError:
            logger.warning("Failed to connect to postgresql")
        finally:
            await database.close()

    @test_wrapper
    def test_check_environment(self) -> Optional[bool]:
        env = self._env_config_model
        if not env.SUBSCRIBE_TELEGRAM_CHANNEL_LINK.strip().replace(' ', ''):
            logger.warning("The SUBSCRIBE_TELEGRAM_CHANNEL_LINK variable is empty, make sure you specify the link")
            return False
        if not env.POSTGRES_PASSWORD:
            logger.warning("The POSTGRES_PASSWORD variable is empty")
            return False

        return True
