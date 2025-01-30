from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    communicating = State()
    in_search = State()


class UserInputState(StatesGroup):
    input_age = State()
