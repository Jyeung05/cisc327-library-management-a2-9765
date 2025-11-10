import pytest
import library_service
import database

def test_valid_borrow():
    success, message = library_service.borrow_book_by_patron("123123", 1)
    assert success == True
    assert "success" in message.lower()

def test_check_patron_id_over_6_digits():
    success, message = library_service.borrow_book_by_patron("1234567", 1)
    assert success == False
    assert "invalid patron id" in message.lower()

def test_check_negative_book_id():
    success, message = library_service.borrow_book_by_patron("123456", -1)
    assert success == False
    assert "not found" in message.lower()

def test_borrow_more_than_5_books():
    for i in range(0,5):
        success, message = library_service.borrow_book_by_patron("123456", i)
    assert success == False
    assert "maximum borrowing limit" in message.lower()

def test_create_borrowing_record_check():
    library_service.borrow_book_by_patron("123456", 1)
    assert 1 in database.get_patron_borrowed_books("123456")

