import argparse
import asyncio
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from dotenv import load_dotenv
from loguru import logger


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-le', nargs='*', help="Load .env")
    return parser.parse_args()


if isinstance(parse_args().le, list):
    if not load_dotenv():
        raise Exception("enviroment file .env not load")
    print(".env loaded")
else:
    print(".env is not loaded")

from src.tests import AnonimChatTests
from src.database import Database
from src.telegram_bot.dialog_loop import dialogs_loop
from src.telegram_bot.handlers import list_handlers
from src.init_data import storage, connect_database_model, env_config_data, config

dp = Dispatcher(storage=storage)
dp.include_routers(*list_handlers)


async def create_database() -> Database:
    database = Database(connect_database_model)

    logger.info("Create database and tables...")
    await database.create_database()

    logger.info("Connecting to database...")
    await database.connect()
    await database.create_tables()
    return database


async def main() -> None:
    bot = Bot(token=env_config_data.TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    logger.info("Starting tests...")
    anon_chat_tests = AnonimChatTests(bot, connect_database_model, env_config_data)
    if not await anon_chat_tests.run_tests():
        return logger.warning("Tests failed.")

    database = await create_database()

    asyncio.create_task(
        dialogs_loop(bot, database, config.config_data.dialog_loop.sleep_time, config.config_data.dialog_loop.max_users,
                     storage))

    logger.info("Set bot commands...")
    await bot.set_my_commands([
        BotCommand(command="start", description="Обновляет бот"),
        BotCommand(command="search", description="Начинает поиск собеседника"),
        BotCommand(command="cancel", description="Завершает общение/поиск"),
        BotCommand(command="set_age", description="Позволяет изменить ваш возраст"),
        BotCommand(command="count_communicating", description="Сколько сейчас общаются пользователей"),
    ])

    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("Get bot info...")
    bot_username = (await bot.get_me()).username

    logger.info("Starting polling...")

    def startup_func():
        if sys.platform == "win32":
            os.system("cls")
        elif sys.platform == "linux":
            os.system("clear")

        logger.info(f"Bot is started: https://t.me/{bot_username}")

    dp.startup.register(startup_func)

    await dp.start_polling(bot, database=database, storage=storage)
    await database.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
