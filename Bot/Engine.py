from functools import wraps

from entities.Player import Player
from entities.User import User
from entities.Room import Room

from exeptions import *
import datetime
import asyncpg

def verbose_player(count):
    word = 'игроков'
    if (count%10 < 5):
        word = 'игрока'
    if (count%10 == 1):
        word = 'игрок' 
    return word

def on_db(func):
    @wraps(func)
    async def _wrapper(*args, **kwargs):
        conn = await asyncpg.connect(database='csfdb', user='postgres',
                                     password='1234', host='localhost')
        try:
            return await func(conn, *args, **kwargs)
        finally:
            await conn.close()

    return _wrapper


async def initialise_db():
    init_conn = await asyncpg.connect(database='postgres', user='postgres',
                                      password='1234', host='localhost')
    if len(await init_conn.fetch("select datname from pg_database where datname = 'csfdb'")) == 0:
        await init_conn.execute(f"create database csfdb")
    await init_conn.close()

    db = await asyncpg.connect(database='csfdb', user='postgres',
                               password='1234', host='localhost')
    # create users table
    await db.execute('create table if not exists users('
                     'telegram_id text primary key,'
                     'username text);')
    # create users_rooms table
    await db.execute('create table if not exists users_rooms('
                     'telegram_id text,'
                     'is_host bool,'
                     'room_id text);')
    # create rooms_info table
    await db.execute('create table if not exists rooms_info('
                     'room_id text primary key,'
                     'room_name text,'
                     'host_id text,'
                     'is_distributed bool,'
                     'player_count int);')
    await db.close()


async def drop_db():
    init_conn = await asyncpg.connect(database='postgres', user='postgres',
                                      password='1234', host='localhost')
    if len(await init_conn.fetch("select datname from pg_database where datname = 'csfdb'")):
        await init_conn.execute(f"drop database csfdb")
    await init_conn.close()


def create_user(user_id, username) -> User:
    return User(telegram_id=user_id, username=username)

#fixme 
@on_db
async def get_room_name(conn, room_id) -> str:
    res = await conn.fetchrow(f"select room_name from rooms_info where room_id = '{room_id}'")
    print(res)
    return res['room_name']


@on_db
async def get_room(conn, room_id) -> Room:
    res = await conn.fetch(
        f"select * from {room_id};"
    )
    room_name = await get_room_name(room_id)

    room = Room(room_id, room_name,
                tuple([Player(
                    line['player_id'], line['name'],
                    line['acceptor_id'], line['disc']) for line in res]
                )
                )
    return room


@on_db
async def register_new_user(conn, telegram_id, username) -> User:
    # create the user
    user = User(telegram_id, username)
    # save it in db
    try:
        await conn.execute(f"insert into users values("
                           f"{user.Telegram_ID}, '{user.Username}')")
    except asyncpg.exceptions.UniqueViolationError:
        raise PlayerIsNotNewError
    return user


@on_db
async def register_new_room(conn, room_name, user_host: User) -> Room:
    room_id = f"h{user_host.Telegram_ID}_{datetime.datetime.now().strftime("%d%m%Y%H%M%S")}"
    await conn.execute(
        f'create table \"{room_id}\"('
        f"  player_id text primary key, "
        f"  name text, "
        f"  acceptor_id text, "
        f"  disc text);")
    q = (
        f"insert into rooms_info values"
        f"('{room_id}', '{room_name}', '{user_host.Telegram_ID}', {False}, {0});")
    print(q)
    await conn.execute(q)

    # сделать хоста игроком
    player = Player(user_host.Telegram_ID, user_host.Username)
    await put_player_in_room(room_id, player, is_host=True)

    room = Room(room_id, room_name)
    room.add_player(player)
    return room


async def validate_room_name(room_name) -> bool:
    restricted_symbols = [",", "`", "\'", "\"", "\\", '--']
    for s in restricted_symbols:
        if s in room_name:
            return False
    return True


@on_db
async def put_player_in_room(conn, room_id, user: User, is_host=False):
    try:
        player = Player(user.Telegram_ID, user.Username)

        await conn.execute(
            f"insert into {room_id} values"
            f"('{player.Telegram_ID}','{player.Username}', "
            f"'{player.Acceptor}', '{player.Disc}');"
        )
        await conn.execute(
            f"update rooms_info set player_count = player_count + 1 where room_id = '{room_id}';"
        )

        await conn.execute(
            f"insert into users_rooms values ('{User.Telegram_ID}', {is_host}, '{room_id}');"
        )

    except asyncpg.exceptions.UndefinedTableError:
        raise RoomDoesNotExistError("Комнаты с таким ключом не существует")
    except asyncpg.exceptions.UniqueViolationError:
        raise PlayerAlreadyJoinedRoomError("Такой игрок уже находится в этой комнате")
    return room_id


@on_db
async def update_room(conn, room: Room):
    for player in room.Players:
        await conn.execute(
            f"insert into {room.ID} "
            f"values ('{player.Telegram_ID}',"
            f"'{player.Username}', '{player.Acceptor}',"
            f"'{player.Disc}') "
            f"on conflict (player_id) do "
            f"update set name = '{player.Username}',"
            f"acceptor_id = '{player.Acceptor}',"
            f"disc = '{player.Disc}' "
            f"where {room.ID}.player_id = '{player.Telegram_ID}';")


@on_db
async def leave_room(conn, room_id, player_id):
    await conn.execute(
        f"delete from {room_id} where player_id = '{player_id}';"
    )
    await conn.fetch(
        f"delete from users_rooms where telegram_id = '{player_id}' and room_id = '{room_id}';"
    )


@on_db
async def get_rooms_where_player(conn, telegram_id):
    quary = (f"select room_id, room_name, host_id, users.username, is_distributed, player_count from rooms_info "
         f"join users on users.telegram_id = rooms_info.host_id "
         f"where room_id in (select room_id from users_rooms where telegram_id = '{telegram_id}') "
         f"or host_id = '{telegram_id}';")
    data = await conn.fetch(quary)
    result = [
        (Room(
            line["room_id"], line["room_name"],
            (Player(
                line["host_id"],
                line["username"]
            ),)
        ), {"is_distributed":line["is_distributed"],
            "player_count": line["player_count"] })
        for line in data]

    return tuple(result)
