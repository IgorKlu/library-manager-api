from fastapi import APIRouter, HTTPException

from app.state import library
from app.schemas.book_schema import BookCreate, BookResponse, BookDeleteRequest

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
        return library.create_book(book_data.title, book_data.author)
    except BookAlreadyExistsError:
        raise HTTPException(status_code=409, detail="Book already exists")

@router.delete("/", response_model=BookResponse)
def delete_book(book_data: BookDeleteRequest):
    try:
        return library.remove_book(book_data.title)
    except BookNotFoundError:
        raise HTTPException(status_code=404, detail="Book not found")
    except BookIsBorrowedError:
        raise HTTPException(status_code=409, detail="Book is currently borrowed")

