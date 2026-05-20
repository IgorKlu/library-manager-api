from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.services.library_db_service import LibraryDBService

from app.db_models.book_model import BookModel

from app.schemas.book_schema import BookResponse

from app.database.connection import get_db

router = APIRouter(
    prefix="/books",
    tags=["books"],
)

service = LibraryDBService()

@router.get("/", response_model=list[BookResponse])
def list_books(db: Session = Depends(get_db)) -> list[BookModel]:
    return service.list_books(db)