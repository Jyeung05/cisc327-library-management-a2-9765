
import pytest
from unittest.mock import Mock

import services.library_service as fees
from services.library_service import pay_late_fees, refund_late_fee_payment
from services.payment_service import PaymentGateway 

# pay_late_fees() TESTS

def test_pay_late_fees_success(mocker):
    mocker.patch(
        "services.library_service.calculate_late_fee_for_book",
        return_value={"fee_amount": 5.0}
    )
    mocker.patch(
        "services.library_service.get_book_by_id",
        return_value={"id": 1, "title": "Test Book"}
    )

    gateway = Mock(spec=PaymentGateway)
    gateway.process_payment.return_value = (True, "txn_123", "Success")

    success, msg, txn = pay_late_fees("123456", 1, gateway)

    assert success is True
    assert "Payment successful" in msg
    assert txn == "txn_123"

    gateway.process_payment.assert_called_once_with(
        patron_id="123456",
        amount=5.0,
        description="Late fees for 'Test Book'"
    )


def test_pay_late_fees_payment_declined(mocker):
    mocker.patch(
        "services.library_service.calculate_late_fee_for_book",
        return_value={"fee_amount": 5.0}
    )
    mocker.patch(
        "services.library_service.get_book_by_id",
        return_value={"id": 1, "title": "Test Book"}
    )

    gateway = Mock(spec=PaymentGateway)
    gateway.process_payment.return_value = (False, None, "Declined")

    success, msg, txn = pay_late_fees("123456", 1, gateway)

    assert success is False
    assert "Payment failed" in msg
    assert txn is None

    gateway.process_payment.assert_called_once_with(
        patron_id="123456",
        amount=5.0,
        description="Late fees for 'Test Book'"
    )


def test_pay_late_fees_invalid_patron_id_does_not_call_gateway(mocker):
    mocker.patch(
        "services.library_service.calculate_late_fee_for_book",
        return_value={"fee_amount": 5.0}
    )
    mocker.patch(
        "services.library_service.get_book_by_id",
        return_value={"id": 1, "title": "Test Book"}
    )

    gateway = Mock(spec=PaymentGateway)

    success, msg, txn = pay_late_fees("12", 1, gateway)

    assert success is False
    assert "Invalid patron ID" in msg
    assert txn is None

    gateway.process_payment.assert_not_called()


def test_pay_late_fees_zero_late_fee_does_not_call_gateway(mocker):
    mocker.patch(
        "services.library_service.calculate_late_fee_for_book",
        return_value={"fee_amount": 0.0}
    )
    mocker.patch(
        "services.library_service.get_book_by_id",
        return_value={"id": 1, "title": "Test Book"}
    )

    gateway = Mock(spec=PaymentGateway)

    success, msg, txn = pay_late_fees("123456", 1, gateway)

    assert success is False
    assert "No late fees to pay" in msg
    assert txn is None

    gateway.process_payment.assert_not_called()


def test_pay_late_fees_handles_gateway_exception(mocker):
    mocker.patch(
        "services.library_service.calculate_late_fee_for_book",
        return_value={"fee_amount": 5.0}
    )
    mocker.patch(
        "services.library_service.get_book_by_id",
        return_value={"id": 1, "title": "Test Book"}
    )

    gateway = Mock(spec=PaymentGateway)
    gateway.process_payment.side_effect = Exception("Network error")

    success, msg, txn = pay_late_fees("123456", 1, gateway)

    assert success is False
    assert "Payment processing error: Network error" in msg
    assert txn is None

    gateway.process_payment.assert_called_once_with(
        patron_id="123456",
        amount=5.0,
        description="Late fees for 'Test Book'"
    )


# refund_late_fee_payment() TESTS

def test_refund_late_fee_payment_success():
    gateway = Mock(spec=PaymentGateway)
    gateway.refund_payment.return_value = (True, "Refunded")

    success, msg = refund_late_fee_payment("txn_999", 5.0, gateway)

    assert success is True
    assert msg == "Refunded"
    gateway.refund_payment.assert_called_once_with("txn_999", 5.0)


@pytest.mark.parametrize("bad_txn", ["", "abc", None, "tx_123"])
def test_refund_late_fee_payment_invalid_transaction_id(bad_txn):
    gateway = Mock(spec=PaymentGateway)

    success, msg = refund_late_fee_payment(bad_txn, 5.0, gateway)

    assert success is False
    assert "Invalid transaction ID" in msg
    gateway.refund_payment.assert_not_called()


@pytest.mark.parametrize("bad_amount", [0, -1, -0.01])
def test_refund_late_fee_payment_invalid_amount_nonpositive(bad_amount):
    gateway = Mock(spec=PaymentGateway)

    success, msg = refund_late_fee_payment("txn_123", bad_amount, gateway)

    assert success is False
    assert "must be greater than 0" in msg
    gateway.refund_payment.assert_not_called()


def test_refund_late_fee_payment_amount_exceeds_max():
    gateway = Mock(spec=PaymentGateway)

    success, msg = refund_late_fee_payment("txn_123", 20.0, gateway)

    assert success is False
    assert "exceeds maximum late fee" in msg
    gateway.refund_payment.assert_not_called()


def test_refund_late_fee_payment_gateway_failure():
    gateway = Mock(spec=PaymentGateway)
    gateway.refund_payment.return_value = (False, "Gateway said no")

    success, msg = refund_late_fee_payment("txn_123", 5.0, gateway)

    assert success is False
    assert "Refund failed: Gateway said no" in msg
    gateway.refund_payment.assert_called_once_with("txn_123", 5.0)


def test_refund_late_fee_payment_gateway_exception():
    gateway = Mock(spec=PaymentGateway)
    gateway.refund_payment.side_effect = Exception("Network down")

    success, msg = refund_late_fee_payment("txn_123", 5.0, gateway)

    assert success is False
    assert "Refund processing error: Network down" in msg
    gateway.refund_payment.assert_called_once_with("txn_123", 5.0)
