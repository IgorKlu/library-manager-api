from fastapi import APIRouter, HTTPException

from app.state import library
from app.schemas.book_schema import BookCreate, BookResponse, BookCopyResponse

from app.exceptions import (
    BookAlreadyExistsError,
    BookNotFoundError,
    BookIsBorrowedError,
)

router = APIRouter(prefix="/books", tags=["books"])

@router.get("/", response_model=list[BookResponse])
def get_books():
    return library.list_books()

@router.post("/", response_model=BookResponse, status_code=201)
def add_book(book_data: BookCreate):
    try:
        return library.create_book(
            book_data.title,
            book_data.author,
            book_data.copies,
        )
    except BookAlreadyExistsError:
        raise HTTPException(status_code=409, detail="Book already exists")

@router.get("/{book_id}/copies", response_model=list[BookCopyResponse])
def show_book_copies(book_id: str):
    book = library.find_book_by_id(book_id)

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return library.find_copies_for_book(book_id)

@router.delete("/{book_id}", response_model=BookResponse)
def delete_book(book_id: str):
    try:
        return library.remove_book(book_id)

    except BookNotFoundError:
        raise HTTPException(status_code=404, detail="Book not found")

    except BookIsBorrowedError:
        raise HTTPException(status_code=409, detail="Book is borrowed")