from pydantic import BaseModel, Field, ConfigDict


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=1000)
    surname: str = Field(min_length=1, max_length=1000)


class UserResponse(BaseModel):
    id: str
    name: str
    surname: str

    model_config = ConfigDict(from_attributes=True)

class UserWithBorrowedCopiesResponse(BaseModel):
    id: str
    name: str
    borrowed_copy_ids: list[str]

    model_config = ConfigDict(from_attributes=True)