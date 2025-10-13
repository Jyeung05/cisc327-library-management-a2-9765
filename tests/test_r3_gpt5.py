import pytest
import library_service as svc
import database as db

def test_borrow_success_decrements_availability(seed_books):
    # Pick a book with stock
    book = next(b for b in seed_books if b["available_copies"] > 0)
    before = book["available_copies"]
    ok, msg = svc.borrow_book_by_patron("123456", book["id"])
    assert ok is True
    after_book = db.get_book_by_id(book["id"])
    assert after_book["available_copies"] == before - 1

@pytest.mark.parametrize("bad_pid", ["", "abc123", "12345", "1234567"])
def test_invalid_patron_id_rejected(seed_books, bad_pid):
    book = seed_books[0]
    ok, msg = svc.borrow_book_by_patron(bad_pid, book["id"])
    assert ok is False
    assert "6" in msg

def test_nonexistent_book_id_rejected(seed_books):
    ok, msg = svc.borrow_book_by_patron("123456", 999999)
    assert ok is False
    assert "not found" in msg.lower()

def test_unavailable_book_rejected(seed_books):
    # Make a single-copy book unavailable by borrowing it, then try again
    single = next(b for b in seed_books if b["total_copies"] == 1)
    ok, _ = svc.borrow_book_by_patron("123456", single["id"])
    assert ok is True
    ok2, msg2 = svc.borrow_book_by_patron("123456", single["id"])
    assert ok2 is False
    assert "not available" in msg2.lower()

def test_borrow_limit_enforced(seed_books, add_book):
    """
    Max 5 books per patron. Borrow 5 distinct, 6th should fail.
    """
    # Ensure at least 6 books exist
    extra = [
        ("Dune", "Frank Herbert", "4444444444445"),
        ("Emma", "Jane Austen", "4444444444446"),
        ("Foundation", "Isaac Asimov", "4444444444447"),
    ]
    for t, a, i in extra:
        add_book(t, a, i, 2)

    all_books = svc.get_all_books()
    first_six_ids = [b["id"] for b in all_books[:6]]

    # Borrow first five
    for bid in first_six_ids[:5]:
        ok, _ = svc.borrow_book_by_patron("999999", bid)
        assert ok is True

    # Sixth should be rejected
    ok6, msg6 = svc.borrow_book_by_patron("999999", first_six_ids[5])
    assert ok6 is False
    assert "maximum borrowing limit" in msg6.lower()
