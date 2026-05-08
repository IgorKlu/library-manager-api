class BookNotFoundError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class BookIsBorrowedError(Exception):
    pass


class BookNotBorrowedError(Exception):
    pass


class UserDoesNotHaveBookError(Exception):
    pass


class BookAlreadyExistsError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    pass

