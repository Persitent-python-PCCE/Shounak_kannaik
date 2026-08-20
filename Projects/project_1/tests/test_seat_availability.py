"""
Seat locking and availability tests.
"""

from common.exceptions import SeatUnavailableError, DuplicateBookingError


def test_seat_exceptions_instantiation():
    """Test that custom exceptions can be raised and caught as expected."""
    try:
        raise SeatUnavailableError("Seat 10A is already occupied")
    except SeatUnavailableError as exc:
        assert str(exc) == "Seat 10A is already occupied"

    try:
        raise DuplicateBookingError("User has already reserved tickets for this schedule")
    except DuplicateBookingError as exc:
        assert str(exc) == "User has already reserved tickets for this schedule"
