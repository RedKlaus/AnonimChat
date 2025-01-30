from aiogram import Bot
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import RedisStorage

from src.telegram_bot.states.user import UserState


async def get_count_communicating_users(storage: RedisStorage, bot: Bot) -> int:
    count = 0
    keys = await storage.redis.keys("fsm:*:*:state")
    for current_user_data in keys:
        _, chat_id, user_id, type_data = current_user_data.decode().split(':')
        current_user_key = StorageKey(bot_id=bot.id, chat_id=int(chat_id), user_id=int(user_id))
        if await storage.get_state(current_user_key) == UserState.communicating:
            count += 1
            continue

    return count
