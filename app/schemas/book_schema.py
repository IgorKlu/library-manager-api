from pydantic import BaseModel, Field, ConfigDict


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=1000)
    author: str = Field(min_length=1, max_length=1000)
    copies_count: int = Field(default=1, ge=1)


class BookResponse(BaseModel):
    id: str
    title: str
    author: str

    model_config = ConfigDict(from_attributes=True)

class BookCopyResponse(BaseModel):
    id: str
    book_id: str
    is_borrowed: bool

    model_config = ConfigDict(from_attributes=True)