from datetime import datetime, timedelta
import library_service as svc
import database as db

def _prep_active_borrow(book_id, patron):
    ok, _ = svc.borrow_book_by_patron(patron, book_id)
    assert ok

def _set_due(patron, book_id, days_overdue):
    # Set due date so that (now - due_date).days == days_overdue
    due = datetime.now() - timedelta(days=days_overdue)
    conn = db.get_db_connection()
    conn.execute(
        """
        UPDATE borrow_records
        SET due_date = ?
        WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
        """,
        (due.isoformat(), patron, book_id),
    )
    conn.commit()
    conn.close()

def test_fee_0_days_overdue(seed_books):
    book = seed_books[0]
    _prep_active_borrow(book["id"], "111111")
    _set_due("111111", book["id"], 0)
    result = svc.calculate_late_fee_for_book("111111", book["id"])
    assert result["days_overdue"] == 0
    assert result["fee_amount"] == 0.00

def test_fee_first_day(seed_books):
    book = seed_books[1]
    _prep_active_borrow(book["id"], "222222")
    _set_due("222222", book["id"], 1)
    result = svc.calculate_late_fee_for_book("222222", book["id"])
    assert result["days_overdue"] == 1
    assert result["fee_amount"] == 0.50

def test_fee_seven_days(seed_books):
    book = seed_books[2]
    _prep_active_borrow(book["id"], "333334")
    _set_due("333334", book["id"], 7)
    result = svc.calculate_late_fee_for_book("333334", book["id"])
    assert result["days_overdue"] == 7
    assert result["fee_amount"] == 3.50

def test_fee_eight_days(seed_books, add_book):
    b = add_book("New", "Auth", "9999999999999", 1)
    _prep_active_borrow(b["id"], "444444")
    _set_due("444444", b["id"], 8)
    result = svc.calculate_late_fee_for_book("444444", b["id"])
    assert result["days_overdue"] == 8
    # 7*0.50 + 1*1.00 = 4.50
    assert result["fee_amount"] == 4.50

def test_fee_cap_at_15(seed_books, add_book):
    b = add_book("Another", "Auth", "8888888888888", 1)
    _prep_active_borrow(b["id"], "555555")
    _set_due("555555", b["id"], 30)
    result = svc.calculate_late_fee_for_book("555555", b["id"])
    assert result["fee_amount"] == 15.00
