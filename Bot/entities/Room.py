from random import shuffle

from entities import Player


class Room:
    def __init__(self, room_id, name=None, players=None):
        if not players:
            players = []
        self.__id = room_id
        self.__name = name
        self.__players: list[Player] = players

    def __str__(self):
        return (f"id: {self.ID}"
                f"players: {len(self.Players)}")

    @property
    def ID(self):
        return self.__id

    @property
    def Name(self):
        return self.__name

    @Name.setter
    def Name(self, value):
        self.__name = value

    @property
    def Players(self):
        return (*self.__players,)

    def add_player(self, player):
        if player not in self.Players:
            self.__players.append(player)

    def distribute(self):
        players: list[Player] = list(self.__players)
        print(players)
        shuffle(players)
        print(players)
        for p in range(len(players)):
            players[p].Acceptor = players[p - 1].Telegram_ID
        self.__players = tuple(players)
