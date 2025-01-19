from aiogram.fsm.state import StatesGroup, State


class MainMenuStates(StatesGroup):
    # nostate_state
    create_state = State()
    conf_create_state = State()
    join_state = State()
    room_name = State()
    room_list = State()

class RoomMenuStates(StatesGroup):
    check_state = State()
    ask_distribute_state = State()

    delete_state = State()

    leave_state = State()

    # mb more


class PlayerStates(StatesGroup):
    Name = State()
    Disc = State()
    # mb more
