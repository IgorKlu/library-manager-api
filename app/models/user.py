from app.models.book import Book


class User:
    def __init__(self,  user_id: int, name: str) -> None:
        self.id = user_id
        self.name = name
        self.borrowed_books: list[Book] = []

    def __repr__(self):
        return f"User(id={self.id}, name={self.name!r})"

