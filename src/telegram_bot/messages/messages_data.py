from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, \
    InlineKeyboardButton, Message, ReplyKeyboardMarkup, KeyboardButton

from src.database import Database
from src.database.models.app_user_model import AppUserModel
from src.database.tables.database_app_user import DatabaseAppUser
from src.database.tables.database_search_params_user import DatabaseSearchParamsUser
from src.telegram_bot.messages.message_data_model import MessageDataModel
from src.telegram_bot.states.user import UserState


def get_start_message() -> MessageDataModel:
    return MessageDataModel(text=f"<b>📨 Анонимный чат</b>",
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text="🔍 Найти собеседника", callback_data="search")],
                                [InlineKeyboardButton(text="⚙️ Параметры поиска", callback_data="search_params")]
                            ]))


def get_search_params_message(app_user_data: AppUserModel, interlocutor_age_text: str) -> MessageDataModel:
    my_age_text: str = str(app_user_data.age) if app_user_data.age is not None else "Не указан"
    return MessageDataModel(text="<b>⚙️ Параметры поиска:</b>\n"
                                 f"- Ваш возраст: <code>{my_age_text}</code>\n"
                                 f"- Возраст собеседника: <code>{interlocutor_age_text}</code>",
                            reply_markup=InlineKeyboardMarkup(
                                inline_keyboard=[
                                    [InlineKeyboardButton(text="✏️ Мой возраст", callback_data="set_my_age")],
                                    [InlineKeyboardButton(text="✏️ Возраст собеседника",
                                                          callback_data="set_interlocutor_age")],
                                    [InlineKeyboardButton(text="◀️ Главное меню", callback_data="start")],
                                ]
                            ))


def get_set_interlocutor_age_message() -> MessageDataModel:
    return MessageDataModel(text="✏️ Выберите возраст собеседника",
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text="до 17 лет",
                                                      callback_data="set_interlocutor_age:0-17")],
                                [InlineKeyboardButton(text="от 18 до 24 лет",
                                                      callback_data="set_interlocutor_age:18-24")],
                                [InlineKeyboardButton(text="от 25 до 32 лет",
                                                      callback_data="set_interlocutor_age:25-32")],
                                [InlineKeyboardButton(text="старше 33 лет",
                                                      callback_data="set_interlocutor_age:33-100")],
                                [InlineKeyboardButton(text="Не имеет значения",
                                                      callback_data="set_interlocutor_age:0-100")],
                                [InlineKeyboardButton(text="⏪ Главное меню", callback_data="start")],
                            ]))


async def send_search_params_message(user_id: int, bot: Bot, database: Database) -> Message:
    app_user = await DatabaseAppUser.init_user_from_telegram_id(database, user_id)
    search_params_data = await (
        await DatabaseSearchParamsUser.init_user(database, app_user.user_id)).get_search_params()
    if search_params_data.interlocutor_age is None:
        interlocutor_age_text = "Не указан"
    else:
        interlocutor_age_text = f"от {search_params_data.interlocutor_age[0]} до {search_params_data.interlocutor_age[-1]} лет"
    message_data = get_search_params_message(await app_user.get_user_data(), interlocutor_age_text)

    return await bot.send_message(user_id, message_data.text, reply_markup=message_data.reply_markup)


async def send_search_event(user_id: int, bot: Bot, state: FSMContext, database: Database) -> Message:
    my_state = await state.get_state()
    reply_markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='✖️ Завершить')]], resize_keyboard=True)
    if my_state == UserState.communicating:
        return await bot.send_message(user_id, "❕ Вы уже находитесь в общении!", reply_markup=reply_markup)
    elif my_state == UserState.in_search:
        return await bot.send_message(user_id, "❕ Вы уже ищете собедника, ожидайте...", reply_markup=reply_markup)

    app_user = await DatabaseAppUser.init_user_from_telegram_id(database, user_id)
    app_user_data = await app_user.get_user_data()
    if app_user_data.age is None:
        await state.clear()
        return await bot.send_message(user_id, "❕ Для продолжения общения укажите ваш возраст - /set_age")

    await state.set_state(UserState.in_search)

    await bot.send_message(user_id, "🔍 Ищу свободного собеседника...", reply_markup=reply_markup)
