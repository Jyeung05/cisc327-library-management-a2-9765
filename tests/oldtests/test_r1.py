import pytest
import library_service

def test_add_book_with_title_over_200_characters():
    long_title = "a" * 201
    success, message = library_service.add_book_to_catalog(long_title, "author", "1234567890123", 1)
    assert success is False
    assert "less than 200" in message.lower()

def test_add_book_with_exactly_200_characters():
    title = "a" * 200
    success, message = library_service.add_book_to_catalog(title, "author", "1234567890123", 1)
    assert success is True
    assert "success" in message.lower()

def test_add_book_with_isbn_over_13_digits():
    isbn = "1" * 14
    success, message = library_service.add_book_to_catalog("title", "author", isbn, 1)
    assert success is False
    assert "13 digits" in message.lower()

def test_add_book_with_isbn_char_input():
    isbn = "a" * 14
    success, message = library_service.add_book_to_catalog("title", "author", isbn, 1)
    assert success is False
    assert "isbn must be numerical digits" in message.lower()

def test_add_book_with_valid_author_input():
    author = "JK Rowling"
    success, message = library_service.add_book_to_catalog("title", author, "1234567890123", 1)
    assert success is True
    assert "success" in message.lower()

def test_add_book_with_less_than_0_copies():
    success, message = library_service.add_book_to_catalog("title", "author", "1234567890123", -1)
    assert success is False
    assert "positive" in message.lower()