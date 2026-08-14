from service.order_service import OrderService
from models.order_model import DirectBuyRequest, CancelOrderRequest

class OrderController:
    def __init__(self):
        self.order_service = OrderService()

    def direct_buy(self, user_id: int, product_id: int, quantity: int):
        request = DirectBuyRequest(user_id=user_id, product_id=product_id, quantity=quantity)
        response = self.order_service.direct_buy(request)
        if response.success:
            print(f"""
------- Order Placed Successfully! -------
Order ID    : {response.order_id}
Status      : {response.status}
Total Price : {response.total_amount}
Order Date  : {response.order_date}
------------------------------------------""")
        else:
            print(f'Error: {response.error_message}')

    # ------------------------------------------------------------------ #
    #  My Orders Menu                                                      #
    # ------------------------------------------------------------------ #

    def _display_orders(self, user_id: int):
        """Fetches and prints the order list. Returns the list of OrderSummaryModel."""
        response = self.order_service.get_orders(user_id)
        if response.error_message:
            print(f'Error: {response.error_message}')
            return []
        if not response.orders:
            print('\nYou have no orders yet.')
            return []

        print(f'\n{"─" * 62}')
        print(f'  {"Order ID":>8}  {"Date":<20} {"Status":<12} {"Total":>10}')
        print(f'{"─" * 62}')
        for o in response.orders:
            print(f'  {o.order_id:>8}  {str(o.order_date):<20} {o.status:<12} {o.total_amount:>10.2f}')
        print(f'{"─" * 62}')
        return response.orders

    def view_orders_menu(self, user_id: int):
        while True:
            orders = self._display_orders(user_id)

            print("""
        1. View order details
        2. Cancel order
        0. Go back
            """)
            choice = input('Enter your choice: ').strip()

            if choice == '1':
                self._view_order_details_menu(user_id)

            elif choice == '2':
                self._prompt_and_cancel(user_id)

            elif choice == '0':
                break
            else:
                print('Invalid choice.')

    def _view_order_details_menu(self, user_id: int):
        try:
            order_id = int(input('Enter Order ID to view: ').strip())
        except ValueError:
            print('Invalid Order ID.')
            return

        response = self.order_service.get_order_details(user_id, order_id)
        if response.error_message:
            print(f'Error: {response.error_message}')
            return

        o = response.order
        print(f'\n{"─" * 62}')
        print(f'  Order ID    : {o.order_id}')
        print(f'  Order Date  : {o.order_date}')
        print(f'  Status      : {o.status}')
        print(f'{"─" * 62}')
        print(f'  {"Product":<28} {"Qty":>5} {"Price":>10} {"Subtotal":>12}')
        print(f'{"─" * 62}')
        for item in response.items:
            print(f'  {item.product_name:<28} {item.quantity:>5} {item.unit_price:>10.2f} {item.subtotal:>12.2f}')
        print(f'{"─" * 62}')
        print(f'  {"Total":>47} {o.total_amount:>12.2f}')
        print(f'{"─" * 62}')

        # Options inside order details
        can_cancel = o.status not in ('completed', 'cancelled')
        if can_cancel:
            print('\n        1. Cancel this order')
        print('        0. Go back')
        sub = input('Enter your choice: ').strip()

        if sub == '1' and can_cancel:
            self._cancel_order(user_id, o.order_id)

    def _prompt_and_cancel(self, user_id: int):
        try:
            order_id = int(input('Enter Order ID to cancel: ').strip())
        except ValueError:
            print('Invalid Order ID.')
            return
        self._cancel_order(user_id, order_id)

    def _cancel_order(self, user_id: int, order_id: int):
        confirm = input(f'Cancel Order #{order_id}? (y/n): ').strip().lower()
        if confirm != 'y':
            print('Cancellation aborted.')
            return
        request = CancelOrderRequest(user_id=user_id, order_id=order_id)
        response = self.order_service.cancel_order(request)
        if response.success:
            print(f'Order #{order_id} has been cancelled and stock has been restored.')
        else:
            print(f'Error: {response.error_message}')

