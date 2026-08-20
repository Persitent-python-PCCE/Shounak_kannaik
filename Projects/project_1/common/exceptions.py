"""
Custom application exception classes.
"""


class SeatUnavailableError(Exception):
    """Raised when an attempt is made to reserve an already booked or locked seat."""
    pass


class DuplicateBookingError(Exception):
    """Raised when a user attempts to place a duplicate booking."""
    pass
