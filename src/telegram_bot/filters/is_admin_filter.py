from aiogram.filters import Filter
from aiogram.types import Message

from src.init_data import env_config_data


class IsAdminFilter(Filter):
    def __init__(self):
        self._admin_telegram_id = env_config_data.ADMIN_TELEGRAM_ID

    def __call__(self, message: Message) -> bool:
        return message.from_user.id == self._admin_telegram_id
