
from common.exceptions import SeatUnavailableError, DuplicateBookingError


def test_seat_exceptions_instantiation():
    try:
        raise SeatUnavailableError("Seat 10A is already occupied")
    except SeatUnavailableError as exc:
        assert str(exc) == "Seat 10A is already occupied"

    try:
        raise DuplicateBookingError("User has already reserved tickets for this schedule")
    except DuplicateBookingError as exc:
        assert str(exc) == "User has already reserved tickets for this schedule"
