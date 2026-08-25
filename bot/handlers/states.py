from aiogram.fsm.state import State, StatesGroup


class ProfileStates(StatesGroup):
    last_name = State()
    first_name = State()
    mid_name = State()
    phone = State()
    address = State()
    email = State()


class OrderStates(StatesGroup):
    comment = State()
