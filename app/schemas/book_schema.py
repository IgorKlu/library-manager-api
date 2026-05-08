from pydantic import BaseModel, Field

class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=1000)
    author: str = Field(min_length=1, max_length=1000)


class BookResponse(BaseModel):
    id: str
    title: str = Field(min_length=1, max_length=1000)
    author: str = Field(min_length=1, max_length=1000)
    is_borrowed: bool

class BorrowBookRequest(BaseModel):
    id: str = Field(min_length=1)


class BookDeleteRequest(BaseModel):
    id: str = Field(min_length=1)
