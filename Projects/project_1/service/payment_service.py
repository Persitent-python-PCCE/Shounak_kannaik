

from config.cache import cache


class PaymentService:

    def __init__(self, payment_dao):
        self.payment_dao = payment_dao

    def __repr__(self):
        return "PaymentService"

    @cache.memoize(timeout=300)
    def get_all_payment_modes(self):
        return self.payment_dao.get_all_payment_modes()

    @cache.memoize(timeout=300)
    def get_all_payment_statuses(self):
        return self.payment_dao.get_all_payment_statuses()
