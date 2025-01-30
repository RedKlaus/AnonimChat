import asyncio

from aiogram import Bot
from aiogram.exceptions import AiogramError
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import RedisStorage
from loguru import logger

from src.database import Database
from src.telegram_bot.dialog_loop._process_single_user import process_single_user
from src.telegram_bot.states.user import UserState


async def dialogs_loop(bot: Bot, database: Database, sleep_time: int, max_users: int, storage: RedisStorage):
    logger.info(f"Dialog loop is started")
    while True:
        keys = await storage.redis.keys("fsm:*:*:state")
        for user_count, current_user_data in enumerate(keys):
            if user_count >= max_users:
                break
            _, chat_id, user_id, _ = current_user_data.decode().split(':')
            current_user_key = StorageKey(bot_id=bot.id, chat_id=int(chat_id), user_id=int(user_id))

            if await storage.get_state(current_user_key) != UserState.in_search:
                continue

            try:
                await process_single_user(bot, database, current_user_key, storage)
            except Exception as _ex:
                logger.exception(
                    f"An unknown error occurred while processing a user in dialogs_loop, "
                    f"with telegram user_id={current_user_key.user_id}, cleared the user state",
                    _ex)
                await storage.set_state(current_user_key, None)
                await storage.set_data(current_user_key, {})
                try:
                    await bot.send_message(current_user_key.user_id,
                                           "⚠️ Мы столкнулись с проблемой, попробуйте найти собеседника позже")
                except AiogramError as _ex:
                    pass

        await asyncio.sleep(sleep_time)
