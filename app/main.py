from app.models.library import Library
from app.models.book import Book
from app.models.user import User
from app.models.library import Library

library = Library()

book = Book("Atomic Habits", "James Clear")

book1 = library.create_book("HAHA", "OK")

print(book1)

print(library.list_books())
