from aiogram.fsm.state import StatesGroup, State


class StateList(StatesGroup):
    # just started
    awaiting_state = State()

    create_state = State()
    create_confirmation_state = State()

    join_state = State()

    delete_state = State()

    leave_state = State()
