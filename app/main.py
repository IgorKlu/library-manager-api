# from fastapi import FastAPI
# from app.routers.books import router as books_router
# from app.routers.users import router as user_router
from app.state import library
#
# app = FastAPI()
#
# app.include_router(books_router)
# app.include_router(user_router)

book = library.create_book("Atomic Habits", "James Clear", copies_count=3)
user = library.create_user("Igor")

print(book)
print(library.find_copies_for_book(book.id))

borrowed_copy = library.borrow_book(user.id, book.id)
print(borrowed_copy)
print(user.borrowed_copy_ids)

returned_copy = library.return_book(user.id, borrowed_copy.id)
print(returned_copy)
print(user.borrowed_copy_ids)

removed_book = library.remove_book(book.id)
print(removed_book)
print(library.list_books())
print(library.book_copies)