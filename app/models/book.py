class Book:
    def __init__(self, title: str, author: str) -> None:
        self.title: str = title
        self.author: str = author
        self.is_borrowed: bool = False

    def __repr__(self):
        return f"Book(title={self.title!r}, author={self.author!r}, is_borrowed={self.is_borrowed!r})"