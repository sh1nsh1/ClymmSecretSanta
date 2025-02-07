from entities.User import User


class Player(User):
    def __init__(self, telegram_id, username, acceptor=None, disc=None):
        super().__init__(telegram_id, username)
        self.__acceptor = acceptor
        self.__disc = disc if disc else "Предпочтения не указаны"

    def __str__(self):
        return f"""
        Telegram_ID = {self._telegram_id}
        Name = {self._username}
        Acc = {self.__acceptor}
        Disc = {self.__disc}
        """

    @property
    def Disc(self):
        return self.__disc

    @Disc.setter
    def Disc(self, Disc):
        self.__disc = Disc

    @property
    def Acceptor(self):
        return self.__acceptor

    @Acceptor.setter
    def Acceptor(self, acceptor):
        self.__acceptor = acceptor

    @property
    def Username(self):
        return self._username

    @Username.setter
    def Username(self, username):
        self._username = username
