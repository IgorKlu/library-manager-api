from app.services.library_service import Library

import pytest

from app.exceptions import BookIsBorrowedError

def test_create_user_adds_user_with_id():
    library = Library()

    user = library.create_user("Adam")

    assert user.id
    assert isinstance(user.id, str)
    assert user.name == "Adam"
    assert len(library.list_users()) == 1

def test_create_book_creates_default_copy():
    library = Library()

    book = library.create_book("Steve Jobs", "Walter Isaacson")
    copies = library.find_copies_for_book(book.id)

    assert book.id
    assert book.title == "Steve Jobs"
    assert book.author == "Walter Isaacson"
    assert len(copies) == 1
    assert all(copy.book_id == book.id for copy in copies)
    assert all(not copy.is_borrowed for copy in copies)

def test_borrow_book_marks_copy_as_borrowed():
    library = Library()

    user = library.create_user("Adam")
    book = library.create_book("Steve Jobs", "Walter Isaacson", copies_count=3)

    borrowed_copy = library.borrow_book(user.id, book.id)
    copies = library.find_copies_for_book(book.id)

    assert borrowed_copy.is_borrowed
    assert borrowed_copy.id in user.borrowed_copy_ids
    assert len(user.borrowed_copy_ids) == 1
    assert sum(copy.is_borrowed for copy in copies) == 1

def test_return_book_marks_copy_as_available():
    library = Library()

    user = library.create_user("Adam")
    book = library.create_book("Steve Jobs", "Walter Isaacson", copies_count=2)
    borrowed_copy = library.borrow_book(user.id, book.id)

    returned_copy = library.return_book(user.id, borrowed_copy.id)
    copies = library.find_copies_for_book(book.id)

    assert not returned_copy.is_borrowed
    assert returned_copy.id not in user.borrowed_copy_ids
    assert len(user.borrowed_copy_ids) == 0
    assert sum(copy.is_borrowed for copy in copies) == 0

def test_remove_book_removes_book_and_its_copies():
    library = Library()

    book = library.create_book("Steve Jobs", "Walter Isaacson", copies_count=2)
    removed_book = library.remove_book(book.id)

    assert removed_book.id == book.id
    assert library.find_book_by_id(book.id) is None
    assert library.find_copies_for_book(book.id) == []

def test_remove_book_raises_error_when_copy_is_borrowed():
    library = Library()

    user = library.create_user("Adam")
    book = library.create_book("Steve Jobs", "Walter Isaacson", copies_count=2)

    library.borrow_book(user.id, book.id)

    with pytest.raises(BookIsBorrowedError):
        library.remove_book(book.id)

    assert library.find_book_by_id(book.id) is not None
    assert len(library.find_copies_for_book(book.id)) == 2