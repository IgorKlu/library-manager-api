from fastapi import APIRouter, HTTPException

from app.state import library
from app.schemas.book_schema import BookCreate, BookResponse

from app.exceptions import (
    BookAlreadyExistsError,
    UserDoesNotHaveBookError,
    BookIsBorrowedError,
    BookNotBorrowedError,
    BookNotFoundError
)

router = APIRouter(prefix="/books", tags=["books"])

@router.get("/", response_model=list[BookResponse])
def get_books():
    return library.list_books()

@router.post("/", response_model=BookResponse)
def add_book(book_data: BookCreate):
    try:
        return library.create_book(book_data.title, book_data.author)
    except BookAlreadyExistsError:
        raise HTTPException(status_code=409, detail="Book already exists")

