from app.models.book import Book
from app.models.user import User
from app.utils.id_generator import generate_id
from app.exceptions import (
    BookAlreadyExistsError,
    BookIsBorrowedError,
    BookNotBorrowedError,
    UserNotFoundError,
    UserAlreadyExistsError,
    UserDoesNotHaveBookError,
    BookNotFoundError,
)


class Library:
    def __init__(self) -> None:
        self.books: list[Book] = []
        self.users: list[User] = []

    def _generate_user_id(self) -> str:
        while True:
            user_id = generate_id()

            if self.find_user_by_id(user_id) is None:
                return user_id

    def _generate_book_id(self) -> str:
        while True:
            book_id = generate_id()

            if self.find_book_by_id(book_id) is None:
                return book_id

    def add_book(self, book: Book) -> None:
        if self.find_book(book.title) is not None:
            raise BookAlreadyExistsError("Book already exists")

        self.books.append(book)

    def register_user(self, user: User) -> None:
        if self.find_user_by_id(user.id) is not None:
            raise UserAlreadyExistsError("User already exists")

        self.users.append(user)

    def find_book(self, title: str) -> Book | None:
        for book in self.books:
            if book.title == title:
                return book

        return None

    def find_user_by_id(self, user_id: str) -> User | None:
        for user in self.users:
            if user.id == user_id:
                return user

        return None

    def find_book_by_id(self, book_id) -> Book | None:
        for book in self.books:
            if book.id == book_id:
                return book

        return None

    def find_users_by_name(self, user_name: str) -> list[User]:
        return [user for user in self.users if user.name == user_name]

    def borrow_book(self, user_id: str, book_id: str) -> Book:
        book = self.find_book_by_id(book_id)
        user = self.find_user_by_id(user_id)

        if book is None:
            raise BookNotFoundError("Book not found")

        if user is None:
            raise UserNotFoundError("User not found")

        if book.is_borrowed:
            raise BookIsBorrowedError("Book is currently borrowed")

        book.is_borrowed = True
        user.borrowed_books.append(book)

        return book

    def return_book(self, user_id: str, book_id: str) -> Book:
        book = self.find_book_by_id(book_id)
        user = self.find_user_by_id(user_id)

        if book is None:
            raise BookNotFoundError("Book not found")

        if user is None:
            raise UserNotFoundError("User not found")

        if not book.is_borrowed:
            raise BookNotBorrowedError("Book is not currently borrowed")

        if book not in user.borrowed_books:
            raise UserDoesNotHaveBookError("Book is not borrowed by this user")

        book.is_borrowed = False
        user.borrowed_books.remove(book)

        return book

    def remove_book(self, title: str) -> Book:
        book = self.find_book(title)

        if book is None:
            raise BookNotFoundError("Book not found")

        if book.is_borrowed:
            raise BookIsBorrowedError("Book is currently borrowed")

        self.books.remove(book)

        return book

    def list_books(self) -> list[Book]:
        return self.books.copy()

    def list_users(self) -> list[User]:
        return self.users.copy()

    def list_user_books(self, user_id: str) -> list[Book]:
        user = self.find_user_by_id(user_id)

        if user is None:
            raise UserNotFoundError("User not found")

        return user.borrowed_books.copy()

    def create_user(self, name: str) -> User:
        user_id = self._generate_user_id()
        user = User(user_id, name)

        self.register_user(user)

        return user

    def create_book(self, title: str, author: str) -> Book:
        book_id = self._generate_book_id()
        book = Book(book_id, title, author)

        self.add_book(book)

        return book
