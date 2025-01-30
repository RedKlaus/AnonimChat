from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from loguru import logger

from src.database import Database
from src.database.tables.database_app_user import DatabaseAppUser
from src.database.tables.database_search_params_user import DatabaseSearchParamsUser
from src.database.tables.database_telegram_user import DatabaseTelegramUser
from src.init_data import env_config_data


class RegistrateMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        database: Database = data["database"]
        telegram_user: User = event.from_user
        is_premium_user = telegram_user.is_premium if telegram_user.is_premium else False

        is_new_user = await self.register_user(
            database=database,
            telegram_user=telegram_user
        )
        if is_new_user:
            # Уведомляем админа
            await event.bot.send_message(env_config_data.ADMIN_TELEGRAM_ID,
                                         "<b>✍️ Зарегестрирован новый пользователь.</b>\n\n"
                                         f"Telegram ID: <code>{telegram_user.id}</code>\n"
                                         f"Username: <code>@{telegram_user.username}</code>\n"
                                         f"First name: <code>{telegram_user.first_name}</code>\n"
                                         f"Is premium: <code>{is_premium_user}</code>\n"
                                         f"Date register: <code> {event.date} </code>")

        return await handler(event, data)

    @staticmethod
    async def register_user(database: Database, telegram_user: User) -> bool:
        count_register = 0
        # Инициализация пользователя Telegram
        tg_user = await DatabaseTelegramUser.init_user_from_id(database, telegram_user.id)
        if not tg_user:
            count_register += 1
            logger.info(f"created telegram user: {telegram_user.id}")
            await DatabaseTelegramUser.init_user_with_create(
                database, telegram_user.id, telegram_user.first_name,
                telegram_user.last_name, telegram_user.username,
                telegram_user.language_code, telegram_user.is_premium,
                telegram_user.added_to_attachment_menu
            )

        # Инициализация пользователя App
        app_user = await DatabaseAppUser.init_user_from_telegram_id(database, telegram_user.id)
        if not app_user:
            count_register += 1
            logger.info(f"created app user: {telegram_user.id}")
            app_user = await DatabaseAppUser.init_user_with_create(database, telegram_user.id)

        # Инициализация параметров поиска
        search_params = await DatabaseSearchParamsUser.init_user(database, app_user.user_id)
        if not search_params:
            count_register += 1
            logger.info(f"created search params user: tgid={telegram_user.id} | appid={app_user.user_id}")
            await DatabaseSearchParamsUser.init_user_with_create(database, app_user.user_id, [0, 100])
        return count_register >= 3
