from pydantic import BaseModel, Field

class BorrowBookRequest(BaseModel):
    book_id: str = Field(min_length=1)
    user_id: str = Field(min_length=1)

class ReturnBookRequest(BaseModel):
    copy_id: str = Field(min_length=1)
    user_id: str = Field(min_length=1)