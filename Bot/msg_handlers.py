from aiogram import Router, types, F
from aiogram.types import ReplyKeyboardRemove

import Strings.Strings
from StateList import MainMenuStates, RoomMenuStates, PlayerStates
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from exeptions import *
from Strings.Strings import *

import Engine
import Keyboards as kb

r = Router()


@r.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext):
    print('start_cmd:', message.from_user.id)
    await state.clear()
    await message.answer(START_STRING)

    try:
        user = await Engine.register_new_user(message.from_user.id, message.from_user.username)

        await message.answer("Видимо вы здесь впервые, записываю вас в базу данных")
    except PlayerIsNotNewError:
        await message.answer("Вижу Ваш аккаунт уже есть в базе данных, с возвращением")
        user = Engine.create_user(message.from_user.id, message.from_user.username)

    await state.update_data({'user': user})
    await message.answer("Доступные действия:", reply_markup=kb.MainMenuRKB())


@r.message(F.text.lower().in_(["отменить", "в меню"]))
@r.callback_query((F.data == 'cancel'))
async def cancel(msg: types.CallbackQuery | types.Message, state: FSMContext):
    if isinstance(msg, types.CallbackQuery):
        await msg.answer()
        msg = msg.message

    curr_state = await state.get_state()
    data = await state.get_data()
    if curr_state in RoomMenuStates and msg.text.lower() != 'в меню':
        word = 'меню комнаты'
        rkb = kb.RoomMenuRKB(str(msg.from_user.id) in data.pop('curr_room').ID)
        await state.set_state(RoomMenuStates.check_state)
    else:
        word = 'главное меню'
        rkb = kb.MainMenuRKB()
        await state.clear()
        await state.set_data(data)

    await msg.answer(Strings.Strings.CANCELED_STRING % word, reply_markup=rkb)

    if curr_state is None:
        return


@r.message(F.text == "Создать новую комнату")
async def ask_create_new_room(msg: types.Message, state: FSMContext):
    print('ask_create_new_room:', msg.from_user.id)
    await msg.answer(ASK_CREATE_CONF_STRING, reply_markup=kb.AskConfirmationRKB('Подтвердить создание комнаты'))
    await state.set_state(MainMenuStates.create_state)


@r.message(F.text == "Подтвердить создание комнаты", MainMenuStates.create_state)
async def ask_new_room_name(msg: types.Message, state: FSMContext):
    print('ask_new_room_name:', msg.from_user.id)
    await msg.answer(Strings.Strings.ASK_ROOM_NAME_STRING, reply_markup=ReplyKeyboardRemove())
    await state.set_state(MainMenuStates.room_name)


@r.message(MainMenuStates.room_name)
async def save_room_name(msg: types.Message, state: FSMContext):
    print('save_room_name:', msg.from_user.id)
    await state.update_data({"room_name": msg.text})
    await state.set_state(MainMenuStates.conf_create_state)
    await msg.answer(Strings.Strings.ASK_CONF_ROOM_NAME_STRING % msg.text,
                     reply_markup=kb.AskConfirmationIKB('Подтвердить', 'room_name'))


@r.callback_query(F.data == "confirm_room_name", MainMenuStates.conf_create_state)
async def create_new_room(msg: types.CallbackQuery, state: FSMContext):
    print('create_new_room:', msg.from_user.id)
    data = await state.get_data()

    if not data.get('user'):
        user_host = Engine.create_user(msg.from_user.id, msg.from_user.username)
    else:
        user_host = data['user']

    room = await Engine.register_new_room(data['room_name'], user_host)

    await msg.message.answer(CREATED_STRING % data['room_name'])
    await msg.message.answer(room.ID, reply_markup=kb.RoomMenuRKB(True))

    await state.update_data({'curr_room': room})
    await state.update_data({'user': user_host})

    await state.set_state(RoomMenuStates.check_state)


@r.message(F.text == "Мои комнаты")
async def my_room_list(msg: types.Message, state: FSMContext):
    print('check_my_rooms:', msg.from_user.id)
    room_names = await Engine.get_rooms_where_player(msg.from_user.id)
    await msg.answer(CHECK_MY_ROOMS_STRING, reply_markup=ReplyKeyboardRemove())
    await msg.answer(ROOM_LIST_STRING,
                     reply_markup=kb.RoomListIKB(await Engine.get_rooms_where_player(msg.from_user.id)))
    await state.set_state(MainMenuStates.room_list)


@r.message(F.text == "Войти в комнату")
async def ask_join_key(msg: types.Message, state: FSMContext):
    print('ask_join_key:', msg.from_user.id)
    await msg.answer(JOIN_STRING, reply_markup=kb.CancelRKB())
    await state.set_state(MainMenuStates.join_state)


@r.message(MainMenuStates.join_state)
async def join_room(msg: types.Message, state: FSMContext):
    print('join_room:', msg.from_user.id)
    data = await state.get_data()

    is_host = (str(msg.from_user.id) in msg.text)

    try:
        if not data.get('curr_room'):
            curr_room = await Engine.get_room(msg.text)
        else:
            curr_room = data.get('curr_room')

        await Engine.put_player_in_room(msg.text, user=data['user'], is_host=is_host)
        await msg.answer(JOIN_SUCCEEDED_STRING, reply_markup=kb.RoomMenuRKB(is_host))

        # notifications
        await msg.bot.send_message(
            msg.text[1:msg.text.find("_")],
            f"{msg.from_user.username} вошёл в комнату \"{curr_room.Name}\", которую вы создали")

    except RoomDoesNotExistError as e:
        await msg.answer(JOIN_FAILED_STRING)
        await msg.answer(e.__str__(), reply_markup=kb.MainMenuRKB())

    except PlayerAlreadyJoinedRoomError as e:
        await msg.answer(e.__str__(), reply_markup=kb.RoomMenuRKB(str(msg.from_user.id) in msg.text))

    await state.set_state(RoomMenuStates.check_state)
    await state.update_data({"curr_room": curr_room})


@r.callback_query(F.data.regexp(r'^h\d+_\d{14}$'), MainMenuStates.room_list)
async def check_room(msg: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get('curr_room'):
        curr_room = await Engine.get_room(msg.data)
    else:
        curr_room = data.get('curr_room')

    await state.update_data({'curr_room': curr_room})
    await msg.message.answer(f'Вы находитесь в комнате \"{curr_room.Name}\"',
                             reply_markup=kb.RoomMenuRKB(str(msg.from_user.id) in curr_room.ID))
    await state.set_state(RoomMenuStates.check_state)


@r.message(F.text.lower() == "список участников", RoomMenuStates.check_state)
async def room_player_list(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    if not data.get('curr_room'):
        curr_room = await Engine.get_room(msg.data)
    else:
        curr_room = data.get('curr_room')
    ans = Strings.Strings.PlAYER_LIST_STRING % curr_room.Name
    for p in curr_room.Players:
        ans += f"    @{p.Username}\n"

    if len(curr_room.Players) % 10 == 1:
        word = 'игрок'
    elif len(curr_room.Players) % 10 in (2, 3, 4):
        word = 'игрока'
    else:
        word = 'игроков'
    ans += f"Всего {len(curr_room.Players)} {word}"
    await msg.answer(ans)


@r.message(F.text.lower() == "провести жеребьевку (создатель)", RoomMenuStates.check_state)
async def ask_distribute(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    if not data.get('curr_room'):
        curr_room = await Engine.get_room(msg.data)
    else:
        curr_room = data.get('curr_room')
    if str(msg.from_user.id) in curr_room.ID:
        await state.set_state(RoomMenuStates.ask_distribute_state)
        await msg.answer(Strings.Strings.ASK_ROOM_DISTRIBUTE_STRING,
                         reply_markup=kb.AskConfirmationIKB('Провести жеребьёвку', 'distribute'))
    else:
        await msg.answer(Strings.Strings.ASK_ROOM_DISTRIBUTE_NON_HOST_STRING, reply_markup=kb.RoomMenuRKB(True))


@r.callback_query(F.data == 'confirm_distribute', RoomMenuStates.ask_distribute_state)
async def distribute(msg: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get('curr_room'):
        curr_room = await Engine.get_room(msg.data)
    else:
        curr_room = data.get('curr_room')

    curr_room.distribute()
    await Engine.update_room(curr_room)
    for p in curr_room.Players:
        await msg.bot.send_message(p.Telegram_ID, Strings.Strings.DISTRIBUTE_SUCCEEDED_STRING % curr_room.Name,
                                   reply_markup=kb.RoomMenuRKB(True))
    await state.set_state(RoomMenuStates.check_state)


@r.message(F.text.lower() == 'узнать моего подопечного', RoomMenuStates.check_state)
async def get_acceptor(msg: types.Message, state: FSMContext):
    print()
    data = await state.get_data()
    if not data.get('curr_room'):
        curr_room = await Engine.get_room()
    else:
        curr_room = data.get('curr_room')
    for p in curr_room.Players:
        if p.Telegram_ID == str(msg.from_user.id):
            acceptor_id = p.Acceptor
            for a in curr_room.Players:
                if a.Telegram_ID == acceptor_id:
                    await msg.answer(Strings.Strings.GET_ACCEPTOR_STRING % (a.Username, a.Disc))
            else:
                await msg.answer(Strings.Strings.EMPTY_ACCEPTOR_STRING)


@r.message(F.text.lower() == 'покинуть комнату', RoomMenuStates.check_state)
async def ask_leave_room(msg: types.Message, state: FSMContext):
    await state.set_state(RoomMenuStates.leave_state)
    await msg.answer(Strings.Strings.ASK_LEAVE_STRING, reply_markup=kb.AskConfirmationRKB('Подтвердить выход'))


@r.message(F.text.lower() == 'подтвердить выход', StateFilter(RoomMenuStates.leave_state))
async def leave_room(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    room = data.pop('curr_room')
    print(data)
    await Engine.leave_room(room.ID, msg.from_user.id)
    await msg.answer(LEAVE_SUCCEEDED_STRING, reply_markup=kb.MainMenuRKB())
    await msg.bot.send_message(
        room.ID[1:room.ID.find('_')],
        f"@{msg.from_user.username} вышел из комнаты \"{room.Name}\", которую вы создали")

    await state.set_data(data)
    await state.clear()

# @r.message(Command("help"))
# async def help_cmd(message: types.Message, state: FSMContext):
#     ...
