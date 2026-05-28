from pydantic import BaseModel, Field, ConfigDict

from datetime import datetime

class BorrowBookRequest(BaseModel):
    book_id: str = Field(min_length=1)
    user_id: str = Field(min_length=1)

class ReturnBookRequest(BaseModel):
    copy_id: str = Field(min_length=1)
    user_id: str = Field(min_length=1)

class BorrowingResponse(BaseModel):
    id: str
    user_id: str
    book_copy_id: str
    borrowed_at: datetime
    returned_at: datetime | None

    model_config = ConfigDict(from_attributes=True)