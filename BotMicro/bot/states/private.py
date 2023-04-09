from aiogram.fsm.state import State, StatesGroup


class EditWords(StatesGroup):
    words = State()


class StrikeLimitState(StatesGroup):
    limit = State()


class IgnoredUserState(StatesGroup):
    full_name = State()