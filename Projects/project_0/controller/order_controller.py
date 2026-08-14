from service.order_service import OrderService
from models.order_model import (
    DirectBuyRequest, CancelOrderRequest, 
    UpdateOrderStatusRequest, CancelOrderByIdRequest
)
from utils.ui import clear_screen, pause
from utils.logger import logger

class OrderController:
    def __init__(self):
        self.order_service = OrderService()

    def direct_buy(self, user_id: int, product_id: int, quantity: int):
        request = DirectBuyRequest(user_id=user_id, product_id=product_id, quantity=quantity)
        response = self.order_service.direct_buy(request)
        if response.success:
            logger.info(f"User {user_id} successfully placed Order #{response.order_id} for Product {product_id} (Qty: {quantity})")
            print(f"""
------- Order Placed Successfully! -------
Order ID    : {response.order_id}
Status      : {response.status}
Total Price : {response.total_amount}
Order Date  : {response.order_date}
------------------------------------------""")
        else:
            logger.error(f"User {user_id} failed to place order for Product {product_id}: {response.error_message}")
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
            clear_screen()
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
                pause()

    def _view_order_details_menu(self, user_id: int):
        try:
            order_id = int(input('Enter Order ID to view: ').strip())
        except ValueError:
            print('Invalid Order ID.')
            pause()
            return

        response = self.order_service.get_order_details(user_id, order_id)
        if response.error_message:
            print(f'Error: {response.error_message}')
            pause()
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
        pause()

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
            pause()
            return
        request = CancelOrderRequest(user_id=user_id, order_id=order_id)
        response = self.order_service.cancel_order(request)
        if response.success:
            logger.info(f"User {user_id} cancelled Order #{order_id}")
            print(f'Order #{order_id} has been cancelled and stock has been restored.')
        else:
            logger.error(f"User {user_id} failed to cancel Order #{order_id}: {response.error_message}")
            print(f'Error: {response.error_message}')
        pause()

    # ------------------------------------------------------------------ #
    #  Admin Orders Management                                             #
    # ------------------------------------------------------------------ #
    
    def _show_all_admin_orders(self):
        """Helper to print all orders without pausing. Returns True if orders exist."""
        response = self.order_service.get_all_orders()
        if response.error_message:
            print(f'Error: {response.error_message}')
            return False
        if not response.orders:
            print('\nNo orders found in the system.')
            return False
            
        print(f'\n{"─" * 85}')
        print(f'  {"Order ID":>8}  {"User":<15} {"Date":<20} {"Status":<12} {"Total":>10}')
        print(f'{"─" * 85}')
        for o in response.orders:
            print(f'  {o.order_id:>8}  {o.username:<15} {str(o.order_date):<20} {o.status:<12} {o.total_amount:>10.2f}')
        print(f'{"─" * 85}')
        return True

    def admin_view_all_orders(self):
        self._show_all_admin_orders()
        pause()

    def admin_search_order(self):
        try:
            order_id = int(input('Enter Order ID to search: ').strip())
        except ValueError:
            print('Invalid Order ID.')
            pause()
            return
            
        response = self.order_service.search_order(order_id)
        if response.error_message:
            print(f'Error: {response.error_message}')
            pause()
            return
            
        if not response.orders:
            print(f'\nOrder #{order_id} not found.')
            pause()
            return
            
        print(f'\n{"─" * 85}')
        print(f'  {"Order ID":>8}  {"User":<15} {"Date":<20} {"Status":<12} {"Total":>10}')
        print(f'{"─" * 85}')
        for o in response.orders:
            print(f'  {o.order_id:>8}  {o.username:<15} {str(o.order_date):<20} {o.status:<12} {o.total_amount:>10.2f}')
        print(f'{"─" * 85}')
        pause()

    def admin_view_order_details(self):
        try:
            order_id = int(input('Enter Order ID to view details: ').strip())
        except ValueError:
            print('Invalid Order ID.')
            pause()
            return

        response = self.order_service.get_admin_order_details(order_id)
        if response.error_message:
            print(f'Error: {response.error_message}')
            pause()
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
        pause()

    def admin_update_order_status(self):
        if not self._show_all_admin_orders():
            pause()
            return

        try:
            order_id = int(input('Enter Order ID to update: ').strip())
        except ValueError:
            print('Invalid Order ID.')
            pause()
            return
            
        status = input('Enter new status (placed, processing, shipped, completed, cancelled): ').strip().lower()
        if not status:
            print('Status cannot be empty.')
            pause()
            return
            
        request = UpdateOrderStatusRequest(order_id=order_id, status=status)
        response = self.order_service.update_order_status(request)
        if response.success:
            logger.info(f"Admin updated Order #{order_id} status to '{status}'")
            print(f'Order #{order_id} status updated to "{status}".')
        else:
            logger.error(f"Admin failed to update Order #{order_id} status: {response.error_message}")
            print(f'Error: {response.error_message}')
        pause()

    def admin_cancel_order(self):
        if not self._show_all_admin_orders():
            pause()
            return

        try:
            order_id = int(input('Enter Order ID to cancel: ').strip())
        except ValueError:
            print('Invalid Order ID.')
            pause()
            return
            
        confirm = input(f'Are you sure you want to cancel Order #{order_id}? This will restore stock. (y/n): ').strip().lower()
        if confirm != 'y':
            print('Cancellation aborted.')
            pause()
            return
            
        request = CancelOrderByIdRequest(order_id=order_id)
        response = self.order_service.admin_cancel_order(request)
        if response.success:
            logger.info(f"Admin cancelled Order #{order_id}")
            print(f'Order #{order_id} has been cancelled and stock has been restored.')
        else:
            logger.error(f"Admin failed to cancel Order #{order_id}: {response.error_message}")
            print(f'Error: {response.error_message}')
        pause()
