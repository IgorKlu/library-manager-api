class Book:
    def __init__(self, book_id: str, title: str, author: str) -> None:
        self.id: str = book_id
        self.title: str = title
        self.author: str = author
        self.is_borrowed: bool = False

    def __repr__(self):
        return (
        f"Book(id={self.id!r}, title={self.title!r},"
        f"author={self.author!r}, is_borrowed={self.is_borrowed!r})"
                )