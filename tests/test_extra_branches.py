# tests/test_library_extra_branches_gpt5.py
import services.library_service as svc


def test_add_book_rejects_blank_author():
    ok, msg = svc.add_book_to_catalog("Title", "   ", "9999999999999", 1)
    assert ok is False
    assert "Author is required" in msg


def test_add_book_rejects_author_over_100_chars():
    long_author = "a" * 101
    ok, msg = svc.add_book_to_catalog("Title", long_author, "8888888888888", 1)
    assert ok is False
    assert "less than 100" in msg


def test_borrow_book_insert_borrow_record_fails(mocker):
    # valid patron and existing book
    mocker.patch("library_service.get_book_by_id", return_value={
        "id": 1,
        "title": "X",
        "available_copies": 1,
        "total_copies": 1,
    })
    mocker.patch("library_service.get_patron_borrow_count", return_value=0)
    # force failure
    mocker.patch("library_service.insert_borrow_record", return_value=False)

    ok, msg = svc.borrow_book_by_patron("123456", 1)
    assert ok is False
    assert "Database error occurred while creating borrow record" in msg


def test_borrow_book_update_availability_fails(mocker):
    mocker.patch("library_service.get_book_by_id", return_value={
        "id": 1,
        "title": "X",
        "available_copies": 1,
        "total_copies": 1,
    })
    mocker.patch("library_service.get_patron_borrow_count", return_value=0)
    mocker.patch("library_service.insert_borrow_record", return_value=True)
    mocker.patch("library_service.update_book_availability", return_value=False)

    ok, msg = svc.borrow_book_by_patron("123456", 1)
    assert ok is False
    assert "Database error occurred while updating book availability" in msg


def test_return_book_update_return_record_fails(mocker):
    mocker.patch("library_service.get_book_by_id", return_value={
        "id": 1,
        "title": "X",
        "available_copies": 0,
        "total_copies": 1,
    })
    # active borrow list will contain the book
    mocker.patch("library_service.get_patron_borrowed_books", return_value=[{
        "book_id": 1,
        "due_date": svc.datetime.now(),
    }])
    mocker.patch("library_service.update_borrow_record_return_date", return_value=False)

    ok, msg = svc.return_book_by_patron("123456", 1)
    assert ok is False
    assert "Database error occurred while updating return record" in msg


def test_calculate_late_fee_falls_back_to_history_closed_record(mocker):
    # no active borrow
    mocker.patch("library_service.get_patron_borrowed_books", return_value=[])
    # fake DB row with return_date
    fake_conn = mocker.Mock()
    fake_conn.execute.return_value.fetchone.return_value = {
        "borrow_date": svc.datetime.now().isoformat(),
        "due_date": (svc.datetime.now() - svc.timedelta(days=3)).isoformat(),
        "return_date": svc.datetime.now().isoformat(),
    }
    fake_conn.close.return_value = None
    mocker.patch("library_service.get_db_connection", return_value=fake_conn)

    res = svc.calculate_late_fee_for_book("123456", 1)
    assert res["status"] == "ok-closed"


def test_calculate_late_fee_falls_back_to_history_ambiguous_open(mocker):
    mocker.patch("library_service.get_patron_borrowed_books", return_value=[])
    fake_conn = mocker.Mock()
    fake_conn.execute.return_value.fetchone.return_value = {
        "borrow_date": svc.datetime.now().isoformat(),
        "due_date": (svc.datetime.now() - svc.timedelta(days=2)).isoformat(),
        "return_date": None,
    }
    mocker.patch("library_service.get_db_connection", return_value=fake_conn)

    res = svc.calculate_late_fee_for_book("123456", 1)
    assert res["status"] == "ok-ambiguous"


def test_calculate_late_fee_db_error_returns_no_record(mocker):
    mocker.patch("library_service.get_patron_borrowed_books", return_value=[])
    mocker.patch("library_service.get_db_connection", side_effect=Exception("db down"))

    res = svc.calculate_late_fee_for_book("123456", 1)
    assert res["status"] == "no-record"


def test_get_patron_status_report_invalid_id():
    rep = svc.get_patron_status_report("123")
    assert rep["status"] == "error"


def test_get_patron_status_report_db_failure_in_history(mocker):
    mocker.patch("library_service.get_patron_borrowed_books", return_value=[])
    mocker.patch("library_service.get_db_connection", side_effect=Exception("db down"))
    rep = svc.get_patron_status_report("123456")
    assert rep["status"] == "ok"
    # history should be empty because of exception
    assert rep["history"] == []
