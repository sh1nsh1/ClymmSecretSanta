class RoomAlreadyExistsError(Exception):
    pass


class RoomDoesNotExistError(Exception):
    pass


class PlayerAlreadyJoinedRoomError(Exception):
    pass


class PlayerIsNotNewError(Exception):
    pass
