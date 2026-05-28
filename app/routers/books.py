from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.services.library_db_service import LibraryDBService

from app.db_models.book_model import BookModel
from app.db_models.book_copy_model import BookCopyModel

from app.schemas.book_schema import (
    BookResponse,
    BookCreate,
    BookCopyResponse,
)

from app.database.connection import get_db

from app.exceptions import (
    BookAlreadyExistsError,
    BookNotFoundError,
    BookCopyNotFoundError,
    BookIsBorrowedError,
)

router = APIRouter(
    prefix="/books",
    tags=["books"],
)

service = LibraryDBService()

@router.get(
    "/",
    response_model=list[BookResponse],
    status_code=status.HTTP_200_OK,
)
def list_books(db: Session = Depends(get_db)) -> list[BookModel]:
    return service.list_books(db)

@router.post(
    "/",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_book(
        book_data: BookCreate,
        db: Session = Depends(get_db)
) -> BookModel:
    try:
        return service.create_book(
            db=db,
            title=book_data.title,
            author=book_data.author,
            copies_count=book_data.copies_count,
        )

    except BookAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )

@router.get(
    "/search",
    response_model=list[BookResponse],
    status_code=status.HTTP_200_OK
)
def search_books(
        title: str | None = None,
        author: str | None = None,
        db: Session = Depends(get_db),
):
    return service.search_books(
        db=db,
        title=title,
        author=author,
    )

@router.get(
    "/{book_id}",
    response_model=BookResponse,
    status_code=status.HTTP_200_OK,
)
def get_book_by_id(
        book_id: str,
        db: Session = Depends(get_db)
) -> BookModel:
    try:
        return service.get_book_by_id(
            db=db,
            book_id=book_id
        )

    except BookNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )

@router.get(
    "/{book_id}/copies",
    response_model=list[BookCopyResponse],
    status_code=status.HTTP_200_OK
)
def find_copies_for_book(
        book_id: str, db: Session = Depends(get_db)
) -> list[BookCopyModel]:
        return service.find_copies_for_book(
            db=db,
            book_id=book_id,
        )

@router.get(
    "/copies/{copy_id}",
    response_model=BookCopyResponse,
    status_code=status.HTTP_200_OK,
)
def get_book_copy_by_id(copy_id: str, db: Session =  Depends(get_db)):
    try:
        return service.get_book_copy_by_id(
            db=db,
            copy_id=copy_id,
        )
    except BookCopyNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error))

@router.post(
    "/{book_id}/copies",
    response_model=BookCopyResponse,
    status_code=status.HTTP_201_CREATED
)
def add_book_copy(book_id: str, db: Session = Depends(get_db)):
    try:
        return service.add_book_copy(
            db=db,
            book_id=book_id
        )
    except BookNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )


@router.get(
    "/{book_id}/copies/available",
    response_model=list[BookCopyResponse],
    status_code=status.HTTP_200_OK
)
def list_available_copies_for_book(
        book_id: str,
        db: Session = Depends(get_db),
):
    try:
        return service.find_copies_for_book(
            db=db,
            book_id=book_id,
        )
    except BookNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )

@router.delete(
    "/{book_id}",
    response_model=BookResponse,
    status_code=status.HTTP_200_OK
)
def remove_book(
        book_id: str,
        db: Session = Depends(get_db),
):
    try:
        return service.remove_book(
            db=db,
            book_id=book_id,
        )
    except BookNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )
    except BookIsBorrowedError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )