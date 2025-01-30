import re

from aiogram import F, Router, Bot
from aiogram.exceptions import AiogramError
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Message

from src.init_data import FORBIDDEN_TEXTS, FORBIDDEN_RE
from src.telegram_bot.states.user import UserState

communicating_router = Router(name="main")


def check_message(message_text: str) -> bool:
    """
    Проверяет сообщение, которое хочет отправить пользователь, на запрещенные слова, символы и т.д.
    :return:
    """
    assert isinstance(message_text, str)

    for forbidden_text in FORBIDDEN_TEXTS:
        if forbidden_text in message_text:
            return False
    for forbidden_re in FORBIDDEN_RE:
        if re.search(forbidden_re, message_text):
            return False
    return True


async def up_storage_ttl_users(my_state: FSMContext, my_data: dict, interlocutor_storage_key: StorageKey,
                               interlocutor_storage_data: dict, storage: RedisStorage):
    # Обновляем таймер удаления состояния и данных пользователя
    await my_state.set_state(UserState.communicating)
    await my_state.set_data(my_data)

    # Так же его собеседника
    await storage.set_state(interlocutor_storage_key, UserState.communicating)
    await storage.set_data(interlocutor_storage_key, interlocutor_storage_data)


async def get_interlocutor_storage(bot: Bot, interlocutor_telegram_id: int, storage: RedisStorage):
    interlocutor_storage_key = StorageKey(bot.id, interlocutor_telegram_id, interlocutor_telegram_id)
    interlocutor_storage_data = await storage.get_data(interlocutor_storage_key)
    return interlocutor_storage_key, interlocutor_storage_data


@communicating_router.message(UserState.communicating, F.content_type.in_({"text", "sticker"}))
async def communicating_handler(message: Message, state: FSMContext, storage: RedisStorage):
    user_data = await state.get_data()

    interlocutor_telegram_id: int | None = user_data.get("interlocutor_telegram_id")
    if interlocutor_telegram_id is None:
        await state.clear()
        return await message.answer("❕ Не могу найти вашего собеседника, попробуйте найти еще раз...")

    interlocutor_key, interlocutor_data = await get_interlocutor_storage(message.bot, interlocutor_telegram_id, storage)

    # Если собеседник по какой то причине уже не состоит в диалоге с этим польователем, то завершаем это общение
    if interlocutor_data["interlocutor_telegram_id"] != message.from_user.id:
        await state.clear()
        return await message.answer("❕ Собеседник уже не состоит с вами в диалоге, попробуйте найти еще раз...")

    await up_storage_ttl_users(state, user_data, interlocutor_key, interlocutor_data, storage)

    if message.text and not check_message(message.text):
        return await message.reply("❕ В вашем сообщении есть запрещенные слова, постарайтесь не отправлять:\n"
                                   "- Ссылки на ресуры\n"
                                   "- Юзернеймы")

    try:
        # Отправляем собеседнику копию этого сообщения
        await message.bot.copy_message(interlocutor_telegram_id, message.from_user.id, message.message_id)

        # Экспериментальная функция для бота: при отправленном сообщение уведомлять реакцией юзера что сообщение отправлено
        # await message.bot.set_message_reaction(message.chat.id, message.message_id, [ReactionTypeEmoji(emoji="🕊")])
    except AiogramError as _ex:
        await message.reply("❕ Ваш текст не был доставлен, попробуйте отправить его ещё раз...")
