from fastapi import APIRouter, HTTPException

from app.state import library
from app.schemas.user_schema import UserCreate, UserResponse, UserWithBorrowedCopiesResponse

from app.exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
    BookNotFoundError,
    BookIsBorrowedError,
    BookNotBorrowedError,
    UserDoesNotHaveBookError,
    NoAvailableCopyError,
    BookCopyNotFoundError,
)

from app.schemas.book_schema import BorrowBookRequest, BookResponse
from app.schemas.book_schema import BookCopyResponse

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


@router.post("/{user_id}/borrowed-books", response_model=BookCopyResponse)
def borrow_book_for_user(user_id: str, book_data: BorrowBookRequest):
    try:
        return library.borrow_book(user_id, book_data.book_id)
    except BookNotFoundError:
        raise HTTPException(status_code=404, detail="Book not found")
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except NoAvailableCopyError:
        raise HTTPException(status_code=409, detail="Book is currently borrowed")

@router.delete("/{user_id}/borrowed-books/{book_copy_id}", response_model=BookCopyResponse)
def return_borrowed_book_copy(user_id: str, book_copy_id: str):
    try:
        return library.return_book(user_id, book_copy_id)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except BookCopyNotFoundError:
        raise HTTPException(status_code=404, detail="Book copy not found")
    except BookNotBorrowedError:
        raise HTTPException(status_code=409, detail="Book not borrowed")
    except UserDoesNotHaveBookError:
        raise HTTPException(status_code=409, detail="User does not have this book")

@router.get("/{user_id}/borrowed-copy-ids", response_model=list[str])
def get_user_book_copies(user_id: str):
    try:
        return library.list_user_borrowed_copy_ids(user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")

@router.get("/search", response_model=list[UserResponse])
def find_user_by_name(name: str):
    return library.find_users_by_name(name)

@router.get("/{user_id}", response_model=UserWithBorrowedCopiesResponse)
def get_user_by_id(user_id: str):
    user = library.find_user_by_id(user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user