# tests/test_payment_service_no_patch.py
import pytest
from services.payment_service import PaymentGateway


@pytest.mark.slow
def test_process_payment_success():
    g = PaymentGateway()
    ok, txn, msg = g.process_payment("123456", 10.0, "Late fees")
    assert ok is True
    assert txn.startswith("txn_")
    assert "processed successfully" in msg


@pytest.mark.slow
def test_process_payment_invalid_amount():
    g = PaymentGateway()
    ok, txn, msg = g.process_payment("123456", 0, "Late fees")
    assert ok is False
    assert txn == ""
    assert msg.startswith("Invalid amount")


@pytest.mark.slow
def test_process_payment_amount_exceeds_limit():
    g = PaymentGateway()
    ok, txn, msg = g.process_payment("123456", 2000.0, "Late fees")
    assert ok is False
    assert txn == ""
    assert "exceeds limit" in msg


@pytest.mark.slow
def test_process_payment_bad_patron_id():
    g = PaymentGateway()
    ok, txn, msg = g.process_payment("12", 10.0, "Late fees")
    assert ok is False
    assert txn == ""
    assert "Invalid patron ID" in msg


@pytest.mark.slow
def test_refund_payment_success():
    g = PaymentGateway()
    ok, msg = g.refund_payment("txn_123456_1700000000", 5.0)
    assert ok is True
    assert "Refund of $5.00 processed successfully" in msg


@pytest.mark.slow
def test_refund_payment_invalid_txn():
    g = PaymentGateway()
    ok, msg = g.refund_payment("bad_txn", 5.0)
    assert ok is False
    assert "Invalid transaction ID" in msg


@pytest.mark.slow
def test_verify_payment_status():
    g = PaymentGateway()
    res = g.verify_payment_status("txn_123456_1700000000")
    assert res["status"] == "completed"
    assert res["transaction_id"].startswith("txn_")
