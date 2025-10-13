import os
from datetime import datetime, timedelta
import pytest

import database as db
import library_service as svc

@pytest.fixture(scope="session")
def tmp_db_path(tmp_path_factory):
    """A unique SQLite file per test session."""
    return tmp_path_factory.mktemp("db") / "library_test.db"

@pytest.fixture(autouse=True)
def fresh_db(tmp_db_path, monkeypatch):
    """
    Before each test:
      - point the database module at a fresh temp DB path
      - init the schema
    """
    monkeypatch.setattr(db, "DATABASE", str(tmp_db_path), raising=False)
    db.init_database()
    yield
    # Clean up file between tests for isolation
    if os.path.exists(tmp_db_path):
        try:
            os.remove(tmp_db_path)
        except PermissionError:
            pass  # Windows can occasionally hold the file briefly

@pytest.fixture
def seed_books():
    """
    Seed a few known books and return their dict rows (as seen by get_all_books()).
    Titles chosen to make alphabetical order deterministic.
    """
    # title, author, isbn, total copies
    books = [
        ("A Tale of Two Cities", "Charles Dickens", "1111111111111", 3),
        ("Brave New World", "Aldous Huxley", "2222222222222", 2),
        ("Catch-22", "Joseph Heller", "3333333333333", 1),
    ]
    for t, a, i, n in books:
        db.insert_book(t, a, i, n, n)
    return svc.get_all_books()

@pytest.fixture
def add_book():
    """Helper to add a book; returns its DB row (dict)."""
    def _add(title, author, isbn, total):
        ok = db.insert_book(title, author, isbn, total, total)
        assert ok
        return db.get_book_by_isbn(isbn)
    return _add

@pytest.fixture
def borrow_helper():
    """Helper to borrow a book via business logic."""
    def _borrow(patron_id: str, book_id: int):
        ok, msg = svc.borrow_book_by_patron(patron_id, book_id)
        assert ok, f"Borrow failed unexpectedly: {msg}"
    return _borrow

@pytest.fixture
def set_due_date():
    """Helper to set the due_date of the most recent borrow for (patron, book)."""
    def _set(patron_id: str, book_id: int, due: datetime):
        conn = db.get_db_connection()
        conn.execute(
            """
            UPDATE borrow_records
            SET due_date = ?
            WHERE id = (
                SELECT id FROM borrow_records
                WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
                ORDER BY borrow_date DESC
                LIMIT 1
            )
            """,
            (due.isoformat(), patron_id, book_id),
        )
        conn.commit()
        conn.close()
    return _set
