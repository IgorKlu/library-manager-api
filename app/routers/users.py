from fastapi import APIRouter, HTTPException, Depends, status
from psycopg.generators import fetch

from app.services.library_db_service import LibraryDBService
from app.schemas.user_schema import (
    UserCreate,
    UserResponse,
    UserWithBorrowedCopiesResponse
)

from app.database.connection import get_db

from sqlalchemy.orm import Session

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

from app.db_models.user_model import UserModel
from app.schemas.borrowing_schema import BorrowingResponse

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

service = LibraryDBService()

@router.get("/", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
def list_users(db: Session = Depends(get_db)) -> list[UserModel]:
    return service.list_users(db)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate ,db: Session = Depends(get_db)) -> UserModel:
    try:
        return service.create_user(
            db=db,
            name=user_data.name,
            surname=user_data.surname,
        )

    except UserAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )

@router.get(
    "/search",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
)
def search_users(
        name: str | None = None,
        surname: str | None = None,
        db: Session = Depends(get_db),
):
    return service.search_users(
        db=db,
        name=name,
        surname=surname,
    )

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK
)
def get_user_by_id(
    user_id: str,
    db: Session = Depends(get_db),
) -> UserModel:
    try:
        return service.get_user_by_id(
            db=db,
            user_id=user_id,
        )

    except UserNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )

@router.get(
    "/{user_id}/borrowings/active",
    response_model=list[BorrowingResponse],
    status_code=status.HTTP_200_OK,
)
def list_user_active_borrowings(
        user_id: str,
        db: Session = Depends(get_db),
):
    try:
        return service.list_user_active_borrowings(
            db=db,
            user_id=user_id,
        )
    except UserNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )