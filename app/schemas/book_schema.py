from pydantic import BaseModel, Field


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=1000)
    author: str = Field(min_length=1, max_length=1000)
    copies: int = Field(default=1, ge=1)


class BookResponse(BaseModel):
    id: str
    title: str
    author: str


class BookCopyResponse(BaseModel):
    id: str
    book_id: str
    is_borrowed: bool


class BorrowBookRequest(BaseModel):
    book_id: str = Field(min_length=1)
