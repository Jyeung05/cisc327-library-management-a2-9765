from datetime import datetime, timedelta
import pytest
import library_service as svc
import database as db

def test_return_success_no_fee(seed_books):
    book = next(b for b in seed_books if b["available_copies"] > 0)
    svc.borrow_book_by_patron("123456", book["id"])
    before = db.get_book_by_id(book["id"])["available_copies"]

    ok, msg = svc.return_book_by_patron("123456", book["id"])
    assert ok is True
    assert "returned" in msg.lower()
    after = db.get_book_by_id(book["id"])["available_copies"]
    assert after == before + 1

@pytest.mark.parametrize("bad_pid", ["", "12345", "1234567", "abc123"])
def test_return_rejects_bad_patron_id(seed_books, bad_pid):
    book = seed_books[0]
    ok, msg = svc.return_book_by_patron(bad_pid, book["id"])
    assert ok is False
    assert "6" in msg

def test_return_rejects_if_not_borrowed(seed_books):
    book = seed_books[0]
    ok, msg = svc.return_book_by_patron("555555", book["id"])
    assert ok is False
    assert "no active borrow" in msg.lower()

def test_return_overdue_fee_in_message(seed_books):
    # Borrow, then push due_date 10 days in the past -> fee 7*0.50 + 3*1.00 = 6.50
    book = next(b for b in seed_books if b["available_copies"] > 0)
    svc.borrow_book_by_patron("333333", book["id"])

    # Set due date to 10 days ago
    conn = db.get_db_connection()
    conn.execute(
        """
        UPDATE borrow_records
        SET due_date = ?
        WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
        """,
        ((datetime.now() - timedelta(days=10)).isoformat(), "333333", book["id"]),
    )
    conn.commit()
    conn.close()

    ok, msg = svc.return_book_by_patron("333333", book["id"])
    assert ok is True
    assert "6.50" in msg
    assert "overdue by 10" in msg.lower()
