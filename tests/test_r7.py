import pytest
import library_service

def test_test_check_borrowed_books():
    library_service.borrow_book_by_patron(123456, 1)
    test = library_service.get_patron_status_report(123456)
    assert len(test['borrowed_books']) == 1

def test_check_late_fee_zero():
    library_service.borrow_book_by_patron(123456, 1)
    test = library_service.get_patron_status_report(123456)
    assert test['late_fee'] == 0

def test_check_if_borrowed_book_is_returne_in_report():
    library_service.borrow_book_by_patron(123456, 1)
    test = library_service.get_patron_status_report(123456)
    assert "The Great Gatsby" in test['borrowed_books']