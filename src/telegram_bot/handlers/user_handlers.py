from aiogram import F, Router
from aiogram.enums import ChatMemberStatus
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from src.database import Database
from src.database.tables.database_app_user import DatabaseAppUser
from src.database.tables.database_search_params_user import DatabaseSearchParamsUser
from src.init_data import env_config_data
from src.ram_data import get_count_communicating_users
from src.telegram_bot.messages.messages_data import get_start_message, send_search_params_message, \
    get_set_interlocutor_age_message, \
    get_search_params_message, send_search_event
from src.telegram_bot.middlewares.registrate_middleware import RegistrateMiddleware
from src.telegram_bot.states.user import UserState, UserInputState

user_router = Router(name="main")
user_router.message.middleware(RegistrateMiddleware())
user_router.callback_query.middleware(RegistrateMiddleware())


# /start
@user_router.message(CommandStart())
@user_router.callback_query(F.data == "start")
async def start_handler(entity: CallbackQuery | Message):
    message_data = get_start_message()
    if isinstance(entity, Message):
        await entity.answer(message_data.text, reply_markup=message_data.reply_markup)
    else:
        await entity.message.edit_text(message_data.text, reply_markup=message_data.reply_markup)


# /count_communicating
@user_router.message(Command("count_communicating"))
async def count_communicating_handler(message: Message, storage: RedisStorage):
    count_users = await get_count_communicating_users(storage, message.bot)
    return await message.reply(
        f"<b>💬 <code>{count_users} пользователей</code> общаются анонимно.</b>")


# /set_age
@user_router.message(Command("set_age"))
@user_router.callback_query(F.data == "set_my_age")
async def set_age_handler(entity: CallbackQuery | Message, state: FSMContext):
    if isinstance(entity, Message):
        await entity.answer("✏️ Введите ваш возраст: ")
    else:
        await entity.message.edit_text("✏️ Введите ваш возраст: ")
    await state.set_state(UserInputState.input_age)


@user_router.message(UserInputState.input_age)
async def input_age_handler(message: Message, state: FSMContext, database: Database):
    app_user = await DatabaseAppUser.init_user_from_telegram_id(database, message.from_user.id)
    if not message.text.isdigit():
        return await message.answer("✏️ Возраст должен быть числом, введите заново: ")
    text_age = int(message.text)
    if text_age <= 9:
        return await message.answer("✏️ Возраст не должен быть меньше 9 лет, введите заново: ")
    if text_age >= 100:
        return await message.answer("✏️ Возраст не должен быть больше 100 лет, введите заново: ")

    await app_user.set_age(text_age)
    await message.answer("✔️ Возраст успешно установлен")
    await state.clear()
    await start_handler(message)


# start search
@user_router.message(Command("search"))
@user_router.callback_query(F.data == "search")
async def callback_search_handler(entity: CallbackQuery | Message, state: FSMContext, database: Database):
    chat_member = await entity.bot.get_chat_member(env_config_data.SUBSCRIBE_TELEGRAM_CHANNEL,
                                                   entity.from_user.id)
    if chat_member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]:
        text = f"❕ Подпишитесь на канал по кнопке снизу, для доступа к общению"
        reply_markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Подписаться", url=env_config_data.SUBSCRIBE_TELEGRAM_CHANNEL_LINK)]
        ])
        if isinstance(entity, Message):
            return await entity.answer(text, reply_markup=reply_markup)
        else:
            return await entity.message.answer(text, reply_markup=reply_markup)

    await send_search_event(entity.from_user.id, entity.bot, state, database)


# search cancel
@user_router.message(F.text.in_({"/cancel", "✖️ Завершить"}), UserState.in_search)
async def in_search_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("✖️ Отменил поиск собеседника", reply_markup=ReplyKeyboardRemove())
    message_data = get_start_message()
    await message.answer(message_data.text, reply_markup=message_data.reply_markup)


# communicating cancel
@user_router.message(F.text.in_({"/cancel", "✖️ Завершить"}), UserState.communicating)
async def communicating_cancel(message: Message, state: FSMContext, storage: RedisStorage):
    user_data = await state.get_data()
    interlocutor_telegram_id: int | None = user_data.get("interlocutor_telegram_id")
    if interlocutor_telegram_id is None:
        await state.clear()
        return await message.answer("❕ Не могу найти вашего собеседника, попробуйте найти еще раз...")
    await state.clear()
    interlocutor_telegram_id_storage_key = StorageKey(message.bot.id, interlocutor_telegram_id,
                                                      interlocutor_telegram_id)
    me_telegram_id_storage_key = StorageKey(message.bot.id, message.from_user.id, message.from_user.id)
    await storage.set_state(interlocutor_telegram_id_storage_key, None)
    await storage.set_data(interlocutor_telegram_id_storage_key, {})

    await storage.set_state(me_telegram_id_storage_key, None)
    await storage.set_data(me_telegram_id_storage_key, {})

    await message.answer("✖️ Завершил общение с собеседником", reply_markup=ReplyKeyboardRemove())
    return await message.bot.send_message(interlocutor_telegram_id, "✖️ Собеседник завершил общение с вами",
                                          reply_markup=ReplyKeyboardRemove())


# search params
@user_router.message(Command("search_params"))
@user_router.callback_query(F.data == "search_params")
async def callback_search_params_handler(entity: CallbackQuery | Message, database: Database):
    if isinstance(entity, Message):
        return await send_search_params_message(entity.from_user.id, entity.bot, database)

    app_user = await DatabaseAppUser.init_user_from_telegram_id(database, entity.from_user.id)
    search_params_data = await (
        await DatabaseSearchParamsUser.init_user(database, app_user.user_id)).get_search_params()
    if search_params_data.interlocutor_age is None:
        interlocutor_age_text = "Не указан"
    else:
        interlocutor_age_text = f"от {search_params_data.interlocutor_age[0]} до {search_params_data.interlocutor_age[-1]} лет"
    message_data = get_search_params_message(await app_user.get_user_data(), interlocutor_age_text)

    await entity.message.edit_text(message_data.text, reply_markup=message_data.reply_markup)


# set interlocutor age
@user_router.callback_query(F.data == "set_interlocutor_age")
async def callback_set_interlocutor_age_handler(callback_query: CallbackQuery):
    message_data = get_set_interlocutor_age_message()
    await callback_query.message.edit_text(message_data.text, reply_markup=message_data.reply_markup)


@user_router.callback_query(F.data.startswith("set_interlocutor_age:"))
async def callback_set_interlocutor_age_input_handler(callback: CallbackQuery, database: Database):
    interlocutor_age_data = [int(i) for i in callback.data.split(":")[-1].split("-")]
    app_user = await DatabaseAppUser.init_user_from_telegram_id(database, callback.from_user.id)
    search_params_user = await DatabaseSearchParamsUser.init_user(database, app_user.user_id)

    await search_params_user.set_interlocutor_age(interlocutor_age_data)

    await callback.answer("✔️ Возраст собеседника успешно установлен")

    message_data = get_start_message()
    await callback.message.edit_text(message_data.text, reply_markup=message_data.reply_markup)
