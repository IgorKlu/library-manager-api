from pydantic import BaseModel, Field
from app.schemas.book_schema import BookResponse


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=1000)


class UserResponse(BaseModel):
    id: str
    name: str = Field(min_length=1, max_length=1000)


class UserWithBooksResponse(BaseModel):
    id: str
    name: str = Field(min_length=1, max_length=1000)
    borrowed_books: list[BookResponse]