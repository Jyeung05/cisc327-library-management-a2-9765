import pytest
import library_service as svc
import database as db

def test_add_book_success(seed_books):
    ok, msg = svc.add_book_to_catalog(
        "Clean Code", "Robert C. Martin", "4444444444444", 3
    )
    assert ok is True
    assert "success" in msg.lower()

@pytest.mark.parametrize("bad_title", ["", "   "])
def test_reject_blank_title(bad_title):
    ok, msg = svc.add_book_to_catalog(bad_title, "Author", "5555555555555", 1)
    assert ok is False
    assert "title is required" in msg.lower()

def test_reject_title_over_200_chars():
    long_title = "a" * 201
    ok, msg = svc.add_book_to_catalog(long_title, "Author", "6666666666666", 1)
    assert ok is False
    assert "less than 200" in msg.lower()

def test_reject_isbn_wrong_length():
    ok, msg = svc.add_book_to_catalog("T", "A", "123456789012", 1)  # 12
    assert ok is False
    assert "13" in msg

def test_reject_total_copies_non_positive():
    ok, msg = svc.add_book_to_catalog("T", "A", "7777777777777", 0)
    assert ok is False
    assert "positive" in msg.lower()

def test_reject_duplicate_isbn(seed_books):
    # ISBN exists in seed: "1111111111111"
    ok, msg = svc.add_book_to_catalog("Another Title", "New Author", "1111111111111", 1)
    assert ok is False
    assert "already exists" in msg.lower()

@pytest.mark.xfail(reason="Spec requires digits-only ISBN; add isbn.isdigit() check to pass.")
def test_reject_isbn_non_digit_when_length_is_13():
    ok, msg = svc.add_book_to_catalog("T", "A", "ABCDEFGHIJKLM", 1)
    assert ok is False
    assert "digits" in msg.lower()
