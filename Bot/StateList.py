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


class PlayerFormStates(StatesGroup):
    edit_form_state = State()
    ask_name = State()
    ask_conf_name = State()
    ask_disc = State()
    ask_conf_disc = State()
    # mb more
