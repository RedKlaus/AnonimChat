from aiogram import Bot
from aiogram.fsm.storage.base import StorageKey


async def send_info_telegram_users(user1: StorageKey, user2: StorageKey, bot: Bot):
    message_text = "💬 Собеседник найден, напишите ему!"
    await bot.send_message(user1.user_id, message_text)
    await bot.send_message(user2.user_id, message_text)
