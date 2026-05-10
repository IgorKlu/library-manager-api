class BookCopy:
    def __init__(self, copy_id: str, book_id: str) -> None:
        self.id: str = copy_id
        self.book_id: str = book_id
        self.is_borrowed: bool = False

    def __repr__(self) -> str:
        return (f"BookCopy(id={self.id!r}, book_id={self.book_id!r}, "
                f"is_borrowed={self.is_borrowed!r})")
