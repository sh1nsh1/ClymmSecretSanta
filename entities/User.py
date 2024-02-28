class User:
    def __init__(self, user_id, user_name):
        self.ID = user_id
        self.Name = user_name
        self.Donner = None
        self.Acceptor = None
        self.Wish = "Предпочтения не указаны"

    # def __str__(self):
    #