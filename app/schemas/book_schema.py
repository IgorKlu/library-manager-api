from pydantic import BaseModel, Field

class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=1000)
    author: str = Field(min_length=1, max_length=1000)


class BookResponse(BaseModel):
    title: str = Field(min_length=1, max_length=1000)
    author: str = Field(min_length=1, max_length=1000)
    is_borrowed: bool

class BorrowBookRequest(BaseModel):
    title: str = Field(min_length=2, max_length=1000)