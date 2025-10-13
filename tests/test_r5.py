import pytest
import library_service

def test_no_late_fee(): 
    test = library_service.calculate_late_fee_for_book(123456, 1)
    assert test['days_overdue'] == 0
    assert test['fee_amount'] == 0