

class SeatUnavailableError(Exception):
    def  __init__(self,message="Seat is already booked or reserved."):
        super().__init__(message)
        self.message = message
        self.status_code = 409
    pass


class DuplicateBookingError(Exception):
    pass
class AuthenticationError(Exception):
    def  __init__(self,message="Authentication Required"):
        super().__init__(message)
        self.message = message
        self.status_code = 401

class AuthorizationError(Exception):
    def  __init__(self,message="You do not have the permission to access this resource"):
        super().__init__(message)
        self.message = message
        self.status_code = 403

class ResourceNotFoundError(Exception):
    def __init__(self, message="Resource not found"):
        super().__init__(message)
        self.message = message
        self.status_code = 404
