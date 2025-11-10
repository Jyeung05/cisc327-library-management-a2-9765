import pytest
import library_service
import database

def test_patron_id_over_6_characters():
    success, message = library_service.return_book_by_patron("1234567", 1)
    assert success == False
    assert "6 digits" in message.lower()

def test_check_negative_book_id():
    success, message = library_service.return_book_by_patron("1234567", -1)
    assert success == False
    assert "negative book id" in message.lower()

def test_verify_book_was_borrowed_by_patron():
    success, message = library_service.return_book_by_patron("1234567", 1)
    assert success == False
    assert "patron has not borrowed this book" in message.lower()

