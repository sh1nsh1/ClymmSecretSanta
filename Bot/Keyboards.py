from aiogram import types
from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

import Engine


def MainMenuRKB():
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="Создать новую комнату", callback_data="create"),
        KeyboardButton(text="Войти в комнату", callback_data="join"),
        KeyboardButton(text="Мои комнаты", callback_data="check"),
    )
    builder.adjust(3, 1)
    return ReplyKeyboardMarkup(keyboard=builder.export(), resize_keyboard=True)


def AskConfirmationRKB(action_text="Подтвердить", action_callbcack=""):
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(
            text=action_text, callback_data="confirm_" + action_callbcack
        ),
        types.KeyboardButton(text="Отменить"),
    )
    builder.adjust(2, 1)
    return ReplyKeyboardMarkup(keyboard=builder.export(), resize_keyboard=True)


def AskConfirmationIKB(action_text="", action_callbcack=""):
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text=action_text, callback_data="confirm_" + action_callbcack
        ),
        types.InlineKeyboardButton(text="Отменить", callback_data="cancel"),
    )
    builder.adjust(2, 1)
    return InlineKeyboardMarkup(inline_keyboard=builder.export())


def RoomListIKB(data):
    builder = InlineKeyboardBuilder()
    for room, metadata in data:
        builder.row(
            types.InlineKeyboardButton(
                text=f'"{room.Name}" от @{room.Players[0].Username} {metadata["player_count"]} '
                f"{Engine.verbose_player(metadata['player_count'])} {'(подготовка)' if not metadata['is_distributed'] else '(игра началась)'}",
                callback_data=f"{room.ID}",
            )
        )
    builder.row(types.InlineKeyboardButton(text="Отменить", callback_data="cancel"))

    return InlineKeyboardMarkup(inline_keyboard=builder.export())


def RoomMenuRKB(is_host: bool = False):
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="Анкета игрока", callback_data="edit_player"),
        KeyboardButton(text="Узнать моего подопечного", callback_data="see_acceptor"),
        width=2,
    )
    builder.row(
        KeyboardButton(text="Покинуть комнату", callback_data="leave_room"),
        KeyboardButton(text="Список участников", callback_data="player_list"),
        width=2,
    )

    # builder.adjust(3, 1)
    if is_host:
        # builder.row(
        #     KeyboardButton(
        #         text="Редактировать комнату (создатель)",
        #         callback_data="edit_room"), )
        builder.row(
            KeyboardButton(
                text="Удалить комнату (создатель)", callback_data="delete_room"
            ),
            KeyboardButton(
                text="Провести жеребьевку (создатель)", callback_data="distribute"
            ),
        )

        builder.row(
            KeyboardButton(text="В меню", callback_data="cancel"),
        )
    return ReplyKeyboardMarkup(keyboard=builder.export(), resize_keyboard=True)


def CancelIKB():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Отменить", callback_data="cancel"))

    return InlineKeyboardMarkup(inline_keyboard=builder.export())


def CancelRKB():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="Отменить", callback_data="cancel"))
    return ReplyKeyboardMarkup(keyboard=builder.export(), resize_keyboard=True)


def PlayerFormRKB():
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="Имя", callback_data="name"),
        types.KeyboardButton(text="Пожелания", callback_data="wishes"),
    )
    builder.row(
        types.KeyboardButton(text="Отменить", callback_data="cancel"),
    )
    return ReplyKeyboardMarkup(keyboard=builder.export(), resize_keyboard=True)
