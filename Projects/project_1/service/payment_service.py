"""
Payment Service.

Handles business logic and lookups for payment modes and transaction statuses.
Receives PaymentDAO via constructor injection to facilitate unit testing with mock DAOs.
"""


from config.cache import cache


class PaymentService:
    """
    Service layer handling payment reference operations.
    """

    def __init__(self, payment_dao):
        """
        Constructor injection of the PaymentDAO dependency.

        :param payment_dao: PaymentDAO instance (or fake/mock DAO in tests)
        """
        self.payment_dao = payment_dao

    def __repr__(self):
        return "PaymentService"

    @cache.memoize(timeout=300)
    def get_all_payment_modes(self):
        """Retrieve all available payment modes."""
        return self.payment_dao.get_all_payment_modes()

    @cache.memoize(timeout=300)
    def get_all_payment_statuses(self):
        """Retrieve all available payment statuses."""
        return self.payment_dao.get_all_payment_statuses()

