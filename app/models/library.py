from app.models.book import Book
from app.models.user import User
from app.models.book_copy import BookCopy
from app.utils.id_generator import generate_id
from app.exceptions import (
    BookAlreadyExistsError,
    BookIsBorrowedError,
    BookNotBorrowedError,
    UserNotFoundError,
    UserAlreadyExistsError,
    UserDoesNotHaveBookError,
    BookNotFoundError,
    BookCopyAlreadyExistsError,
    NoAvailableCopyError,
    BookCopyNotFoundError
)


class Library:
    def __init__(self) -> None:
        self.books: list[Book] = []
        self.users: list[User] = []
        self.book_copies: list[BookCopy] = []

    # Generate ID and make sure it doesn't already exist
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

    def _generate_book_copy_id(self) -> str:
        while True:
            book_copy_id = generate_id()

            if self.find_book_copy_by_id(book_copy_id) is None:
                return book_copy_id

    def add_book(self, book: Book) -> None:
        if self.find_book_by_title(book.title) is not None:
            raise BookAlreadyExistsError("Book already exists")

        self.books.append(book)

    def add_book_copy(self, book_copy: BookCopy) -> None:
        if self.find_book_copy_by_id(book_copy.id) is not None:
            raise BookCopyAlreadyExistsError("Book copy already exists")

        if self.find_book_by_id(book_copy.book_id) is None:
            raise BookNotFoundError("Book not found")

        self.book_copies.append(book_copy)

    def register_user(self, user: User) -> None:
        if self.find_user_by_id(user.id) is not None:
            raise UserAlreadyExistsError("User already exists")

        self.users.append(user)

    def find_book_by_title(self, title: str) -> Book | None:
        for book in self.books:
            if book.title == title:
                return book

        return None

    def find_user_by_id(self, user_id: str) -> User | None:
        for user in self.users:
            if user.id == user_id:
                return user

        return None

    def find_users_by_name(self, user_name: str) -> list[User]:
        return [user for user in self.users if user.name == user_name]

    def find_book_by_id(self, book_id) -> Book | None:
        for book in self.books:
            if book.id == book_id:
                return book

        return None

    def find_book_copy_by_id(self, book_copy_id: str) -> BookCopy | None:
        for existing_copy in self.book_copies:
            if existing_copy.id == book_copy_id:
                return existing_copy

        return None

    def find_copies_for_book(self, book_id: str) -> list[BookCopy]:
        return [copy for copy in self.book_copies if copy.book_id == book_id]

    def find_available_copy_for_book(self, book_id: str) -> BookCopy | None:
        for existing_copy in self.book_copies:
            if existing_copy.book_id == book_id and not existing_copy.is_borrowed:
                return existing_copy

        return None

    def borrow_book(self, user_id: str, book_id: str) -> BookCopy:
        user = self.find_user_by_id(user_id)

        if user is None:
            raise UserNotFoundError("User not found")

        book = self.find_book_by_id(book_id)

        if book is None:
            raise BookNotFoundError("Book not found")

        available_copy = self.find_available_copy_for_book(book_id)

        if available_copy is None:
            raise NoAvailableCopyError("No available copy found")

        user.borrowed_copy_ids.append(available_copy.id)
        available_copy.is_borrowed = True

        return available_copy



    def return_book(self, user_id: str, copy_id: str) -> BookCopy:
        user = self.find_user_by_id(user_id)

        if user is None:
            raise UserNotFoundError("User not found")

        book_copy = self.find_book_copy_by_id(copy_id)

        if book_copy is None:
            raise BookCopyNotFoundError("Book copy not found")

        if not book_copy.is_borrowed:
            raise BookNotBorrowedError("Book not borrowed")

        if copy_id not in user.borrowed_copy_ids:
            raise UserDoesNotHaveBookError("User does not have a copy of this book")

        book_copy.is_borrowed = False
        user.borrowed_copy_ids.remove(copy_id)

        return book_copy

    def remove_book(self, book_id: str) -> Book:
        book = self.find_book_by_id(book_id)

        if book is None:
            raise BookNotFoundError("Book not found")

        book_copies = self.find_copies_for_book(book.id)

        for book_copy in book_copies:
            if book_copy.is_borrowed:
                raise BookIsBorrowedError("Book is currently borrowed")

        self.book_copies = [
            book_copy
            for book_copy in self.book_copies
            if book_copy.book_id != book_id
        ]

        self.books.remove(book)

        return book

    def list_books(self) -> list[Book]:
        return self.books.copy()

    def list_users(self) -> list[User]:
        return self.users.copy()

    def list_user_borrowed_copy_ids(self, user_id: str) -> list[str]:
        user = self.find_user_by_id(user_id)

        if user is None:
            raise UserNotFoundError("User not found")

        return user.borrowed_copy_ids.copy()

    def create_user(self, name: str) -> User:
        user_id = self._generate_user_id()
        user = User(user_id, name)

        self.register_user(user)

        return user

    def create_book(self, title: str, author: str, copies_count: int = 1) -> Book:
        if copies_count < 1:
            raise ValueError("Copies must be at least 1")

        book_id = self._generate_book_id()
        book = Book(book_id, title, author)

        self.add_book(book)

        for _ in range(copies_count):
            book_copy_id = self._generate_book_copy_id()
            copy_of_book = BookCopy(book_copy_id, book.id)
            self.add_book_copy(copy_of_book)

        return book