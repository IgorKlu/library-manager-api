from fastapi import APIRouter, HTTPException

from app.state import library
from app.schemas.user_schema import UserCreate, UserResponse

from app.exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
    BookNotFoundError,
    BookIsBorrowedError,
    BookNotBorrowedError,
    UserDoesNotHaveBookError,
)

from app.schemas.book_schema import BorrowBookRequest, BookResponse

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=list[UserResponse])
def get_users():
    return library.list_users()

@router.post("/", response_model=UserResponse, status_code=201)
def add_user(user_data: UserCreate):
    try:
        return library.create_user(user_data.name)
    except UserAlreadyExistsError:
        raise HTTPException(status_code=409, detail="User already exists")


@router.post("/{user_id}/borrowed-books", response_model=BookResponse)
def book_borrow(user_id: int, book_data: BorrowBookRequest):
    try:
        return library.borrow_book(user_id, book_data.title)
    except BookNotFoundError:
        raise HTTPException(status_code=404, detail="Book not found")
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except BookIsBorrowedError:
        raise HTTPException(status_code=409, detail="Book is currently borrowed")


@router.get("/{user_id}/books", response_model=list[BookResponse])
def get_user_books(user_id: int):
    try:
        return library.list_user_books(user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")

@router.delete("/{user_id}/borrowed-books", response_model=BookResponse)
def return_borrowed_book(user_id: int, book_data: BorrowBookRequest):
    try:
        return library.return_book(user_id, book_data.title)
    except BookNotFoundError:
        raise HTTPException(status_code=404, detail="Book not found")
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except BookNotBorrowedError:
        raise HTTPException(status_code=409, detail="Book not borrowed")
    except UserDoesNotHaveBookError:
        raise HTTPException(status_code=409, detail="User does not have this book")
