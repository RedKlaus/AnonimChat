from typing import Optional, List

from aiogram import Bot
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import RedisStorage
from loguru import logger

from src.database import Database
from src.database.tables.database_app_user import DatabaseAppUser
from src.database.tables.database_search_params_user import DatabaseSearchParamsUser
from src.telegram_bot.dialog_loop.utils import send_info_telegram_users
from src.telegram_bot.states.user import UserState


async def find_interlocutor(my_user: StorageKey, my_user_age: int, interlocutor_age: Optional[List[int]],
                            database: Database, storage: RedisStorage, bot: Bot) -> Optional[StorageKey]:
    if len(interlocutor_age) != 2:
        logger.warning(
            "У пользователя не верно указан желаемый возраст собеседника, а именно длина списка ОТ и ДО не равна двум (2)")
        return None

    keys = await storage.redis.keys("fsm:*:*:state")
    for user_data in keys:
        _, chat_id, user_id, _ = user_data.decode().split(':')
        user_key = StorageKey(bot_id=bot.id, chat_id=int(chat_id), user_id=int(user_id))

        if user_key == my_user:
            continue

        # Если пользователь в поиске собеседника то добавим его в список
        user_state = await storage.get_state(user_key)
        if user_state == UserState.in_search:
            if not interlocutor_age:
                return user_key

            find_app_user = await DatabaseAppUser.init_user_from_telegram_id(database, user_key.user_id)
            if find_app_user is None:
                logger.warning(
                    f"Пользователь с telegram user_id={user_key.user_id} не был найден в базе данных DatabaseAppUser")
                continue

            interlocutor_user_search_params = await DatabaseSearchParamsUser.init_user(database, find_app_user.user_id)
            if interlocutor_user_search_params is None:
                logger.warning(
                    f"Пользователь с app user_id={find_app_user.user_id} не был найден в базе данных DatabaseSearchParamsUser")
                continue

            interlocutor_user_search_params_data = await interlocutor_user_search_params.get_search_params()

            find_app_user_data = await find_app_user.get_user_data()
            if find_app_user_data.age is None:
                continue

            if interlocutor_age[0] <= find_app_user_data.age <= interlocutor_age[-1]:
                if interlocutor_user_search_params_data.interlocutor_age[0] <= my_user_age <= \
                        interlocutor_user_search_params_data.interlocutor_age[-1]:
                    return user_key


async def process_single_user(bot: Bot, database: Database, current_user_key: StorageKey, storage: RedisStorage):
    keys = await storage.redis.keys("fsm:*:*:state")
    if len(keys) <= 1:
        return

    interlocutor_data_key = "interlocutor_telegram_id"

    database_app_user = await DatabaseAppUser.init_user_from_telegram_id(database, current_user_key.user_id)
    if not database_app_user:
        return

    user_data = await database_app_user.get_user_data()
    if not user_data or user_data.age is None:
        return

    search_params_user = await DatabaseSearchParamsUser.init_user(database, database_app_user.user_id)
    if not search_params_user:
        return

    search_params = await search_params_user.get_search_params()
    if not search_params:
        return

    interlocutor = await find_interlocutor(
        current_user_key,
        user_data.age,
        search_params.interlocutor_age,
        database, storage, bot
    )
    if not interlocutor:
        return

    if await storage.get_state(interlocutor) != UserState.in_search:
        return

    # Устанавливаем состояние общения и данные собеседников
    await storage.set_state(current_user_key, UserState.communicating)
    await storage.set_state(interlocutor, UserState.communicating)

    await storage.set_data(current_user_key, {interlocutor_data_key: interlocutor.user_id})
    await storage.set_data(interlocutor, {interlocutor_data_key: current_user_key.user_id})

    await send_info_telegram_users(current_user_key, interlocutor, bot)
