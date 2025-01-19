class User:
    def __init__(self, telegram_id, username="no name"):
        self._telegram_id = telegram_id
        self._username = username

    def __str__(self):
        return f"tg_id: {self._telegram_id}\n" \
               f"name: {self._username}"

    @property
    def Telegram_ID(self):
        return self._telegram_id

    @property
    def Username(self):
        return self._username
