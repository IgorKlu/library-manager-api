from fastapi import APIRouter, HTTPException, status, Depends

from app.schemas.book_schema import BookCopyResponse
from app.schemas.borrowing_schema import BorrowBookRequest, ReturnBookRequest

from app.database.connection import get_db

from app.services.library_db_service import LibraryDBService

from sqlalchemy.orm import Session

service = LibraryDBService()

from app.exceptions import (
    UserNotFoundError,
    BookNotFoundError,
    BookCopyNotFoundError,
    BorrowingNotFoundError,
)

router = APIRouter(
    prefix="/borrowings",
    tags=["borrowings"]
)

@router.post(
    "/",
    response_model=BookCopyResponse,
    status_code=status.HTTP_201_CREATED
)
def borrow_book(borrow_data: BorrowBookRequest, db: Session = Depends(get_db)):
    try:
        return service.borrow_book(
            db=db,
            user_id=borrow_data.user_id,
            book_id=borrow_data.book_id,
        )
    except UserNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )
    except BookNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )
    except BookCopyNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )

@router.post(
    "/return",
    response_model=BookCopyResponse,
    status_code=status.HTTP_201_CREATED
)
def return_book(return_data: ReturnBookRequest, db: Session = Depends(get_db)):
    try:
        return service.return_book_copy(
            db=db,
            user_id=return_data.user_id,
            copy_id=return_data.copy_id,
        )
    except UserNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    except BookCopyNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )
    except BorrowingNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )