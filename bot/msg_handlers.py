from aiogram import Router, types
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext

from Strings.Strings import *

r = Router()


@r.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext):
    """
    Handles the /start command. Notifies user and puts
    bot into awaiting_state
    """
    await message.answer(START_STRING)
    await state.set_state("awaiting_state")
    # todo show keyboard


@r.message(Command("create"), StateFilter("awaiting_state"))
async def create_cmd(message: types.Message, state: FSMContext):
    """
    Handles the /create command. Notifies user and puts
    bot into create_state
    """
    await message.answer(CREATE_STRING)
    await state.set_state("create_state")


@r.message(Command("yes", 'no'), StateFilter("create_state"))
async def create_confirmation(message: types.Message, state: FSMContext):
    """
    Demands /yes and /no commands to confirm creating a playing room.

    if /yes notifies user and creates the playing room
    if /no notifies user
    puts bot into awaiting_state
    """
    if message.text == "yes":
        await message.answer(CREATE_ACCEPTED_STRING)
        # todo create the room
    else:
        await message.answer(CREATE_CANCELED_STRING)

    await state.set_state("awaiting_state")


@r.message(Command("delete"), StateFilter("create_state"))
async def delete_cmd(message: types.Message, state: FSMContext):
    """
    Handles /delete command. Notifies user and puts
    bot into delete_state
    """
    await message.answer(DELETE_STRING)
    await state.set_state("delete_state")


@r.message(StateFilter("delete_state"))
async def delete_confirmation(message: types.Message, state: FSMContext):
    """
    Demands the playing room key to confirm deleting the playing room.
    If the user is the host and key matches, notifies all participants,
    deletes the playing room and puts bot into awaiting_state
    """
    # todo check if room exists and if user is a host
    if message.text == "key":
        await message.answer(DELETE_SUCCEEDED_STRING)
        # todo delete the room
    else:
        await message.answer(DELETE_FAILED_STRING)

    await state.set_state("awaiting_state")


@r.message(Command("join"), StateFilter("awaiting_state"))
async def join_cmd(message: types.Message, state: FSMContext):
    """
    Handles /join command. Notifies user and puts
    bot into join_state
    """
    await message.answer(JOIN_STRING)
    await state.set_state("join_state")


@r.message(StateFilter("join_state"))
async def get_join_key(message: types.Message, state: FSMContext):
    """
    Demands the playing room key to confirm joining the playing room.
    If the key matches, creates the User in the playing room
    and puts bot into awaiting_state
    """
    # todo key_matching_check
    if message.text == "key":
        await message.answer(JOIN_SUCCEEDED_STRING)
        # todo create User
        
    else:
        await message.answer(JOIN_FAILED_STRING)
    await state.set_state("awaiting_state")


@r.message(StateFilter("awaiting_state"))
async def leave_cmd(message: types.Message, state: FSMContext):
    """
    Handles /leave command. Notifies user and puts bot
    into leave_state
    """
    await message.answer(LEAVE_STRING)
    await state.set_state('leave_state')


@r.message(StateFilter("leave_state"))
async def get_leave_key(message: types.Message, state: FSMContext):
    """
    Demands the playing room key to confirm leaving the playing room.
    If the key matches, deletes the User in the playing room,
    if it does not, notifies user

    Puts bot into awaiting_state
    """
    # todo key_matching_check
    if message.text == "key":
        await message.answer(LEAVE_SUCCEEDED_STRING)
        # todo delete user from playing room
        ...
    else:
        await message.answer(LEAVE_FAILED_STRING)
    await state.set_state("awaiting_state")

# @r.message(Command("help"))
# async def help_cmd(message: types.Message, state: FSMContext):
#     ...