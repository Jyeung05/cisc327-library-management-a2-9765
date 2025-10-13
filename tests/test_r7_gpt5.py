from datetime import datetime, timedelta
import library_service as svc
import database as db

def _fee_for_days(d):
    # mirror of policy for assertions
    if d <= 0: return 0.0
    first7 = min(d, 7)
    rest = max(d - 7, 0)
    return min(first7 * 0.50 + rest * 1.00, 15.00)

def test_report_after_one_borrow_no_fee(seed_books):
    book = next(b for b in seed_books if b["available_copies"] > 0)
    ok, _ = svc.borrow_book_by_patron("121212", book["id"])
    assert ok

    rep = svc.get_patron_status_report("121212")
    assert rep["status"] == "ok"
    assert rep["current_borrow_count"] == 1
    assert rep["total_late_fees"] == 0.00
    assert len(rep["currently_borrowed"]) == 1
    assert rep["currently_borrowed"][0]["title"] == book["title"]

def test_report_includes_overdue_fee_and_history(seed_books):
    book = next(b for b in seed_books if b["available_copies"] > 0)
    svc.borrow_book_by_patron("131313", book["id"])

    # Make it 3 days overdue
    conn = db.get_db_connection()
    conn.execute(
        """
        UPDATE borrow_records
        SET due_date = ?
        WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
        """,
        ((datetime.now() - timedelta(days=3)).isoformat(), "131313", book["id"]),
    )
    conn.commit()
    conn.close()

    rep = svc.get_patron_status_report("131313")
    assert rep["current_borrow_count"] == 1
    assert rep["total_late_fees"] == _fee_for_days(3)
    assert rep["currently_borrowed"][0]["days_overdue"] >= 3

    # Now return it (history should include the entry with return_date)
    ok, _ = svc.return_book_by_patron("131313", book["id"])
    assert ok

    rep2 = svc.get_patron_status_report("131313")
    assert rep2["current_borrow_count"] == 0
    # There should be at least one history item with a return_date
    assert any(item["return_date"] is not None for item in rep2["history"])
