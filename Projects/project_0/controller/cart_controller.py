from service.cart_service import CartService
from models.cart_model import (
    AddToCartRequest,
    UpdateCartItemRequest,
    RemoveCartItemRequest,
    CheckoutCartRequest
)
from utils.ui import clear_screen, pause

class CartController:
    def __init__(self):
        self.cart_service = CartService()

    def add_to_cart(self, user_id: int, product_id: int, quantity: int):
        request = AddToCartRequest(user_id=user_id, product_id=product_id, quantity=quantity)
        response = self.cart_service.add_to_cart(request)
        if response.success:
            print('Product added to cart successfully!')
        else:
            print(f'Error: {response.error_message}')

    def _display_cart(self, user_id: int):
        """Fetches and prints the cart. Returns the ViewCartResponse."""
        response = self.cart_service.view_cart(user_id)
        if response.error_message:
            print(f'Error loading cart: {response.error_message}')
            return response
        if not response.items:
            print('\nYour cart is empty.')
            return response

        print(f'\n{"─" * 65}')
        print(f'  {"Product":<30} {"Qty":>5} {"Price":>10} {"Subtotal":>12}')
        print(f'{"─" * 65}')
        for item in response.items:
            print(f'  {item.product_name:<30} {item.quantity:>5} {item.unit_price:>10.2f} {item.subtotal:>12.2f}')
        print(f'{"─" * 65}')
        print(f'  {"Total":>48} {response.total_amount:>12.2f}')
        print(f'{"─" * 65}')
        return response

    def view_cart_menu(self, user_id: int):
        while True:
            clear_screen()
            cart = self._display_cart(user_id)

            print("""
        1. Checkout cart
        2. Update cart
        0. Go back
            """)
            choice = input('Enter your choice: ').strip()

            if choice == '1':
                self._checkout(user_id)
                pause()
                break  # Return to user menu after checkout

            elif choice == '2':
                self._update_cart_menu(user_id, cart)

            elif choice == '0':
                break
            else:
                print('Invalid choice.')
                pause()

    def _update_cart_menu(self, user_id: int, cart):
        if not cart.items:
            return

        print("""
        1. Update product quantity
        2. Remove product from cart
        0. Back
        """)
        choice = input('Enter your choice: ').strip()

        if choice == '1':
            name = input('Enter the product name to update quantity: ').strip()
            item = self._find_item_in_cart(cart.items, name)
            if item is None:
                print(f"No item named '{name}' found in your cart.")
                pause()
                return
            try:
                new_qty = int(input(f'Enter new quantity (current: {item.quantity}): ').strip())
                if new_qty <= 0:
                    print('Quantity must be greater than zero.')
                    pause()
                    return
            except ValueError:
                print('Invalid quantity.')
                pause()
                return
            req = UpdateCartItemRequest(user_id=user_id, product_id=item.product_id, new_quantity=new_qty)
            res = self.cart_service.update_cart_item(req)
            if res.success:
                print('Cart updated successfully.')
            else:
                print(f'Error: {res.error_message}')
            pause()

        elif choice == '2':
            name = input('Enter the product name to remove: ').strip()
            item = self._find_item_in_cart(cart.items, name)
            if item is None:
                print(f"No item named '{name}' found in your cart.")
                pause()
                return
            req = RemoveCartItemRequest(user_id=user_id, product_id=item.product_id)
            res = self.cart_service.remove_cart_item(req)
            if res.success:
                print(f"'{item.product_name}' removed from cart.")
            else:
                print(f'Error: {res.error_message}')
            pause()

        elif choice == '0':
            return
        else:
            print('Invalid choice.')
            pause()


    def _find_item_in_cart(self, items: list, name: str):
        """Case-insensitive exact match against cart items."""
        for item in items:
            if item.product_name.strip().lower() == name.strip().lower():
                return item
        return None

    def _checkout(self, user_id: int):
        confirm = input('Confirm checkout? (y/n): ').strip().lower()
        if confirm != 'y':
            print('Checkout cancelled.')
            return
        req = CheckoutCartRequest(user_id=user_id)
        res = self.cart_service.checkout_cart(req)
        if res.success:
            print(f"""
------- Order Placed Successfully! -------
Order ID    : {res.order_id}
Status      : {res.status}
Total Price : ${res.total_amount}
Order Date  : {res.order_date}
------------------------------------------""")
        else:
            print(f'Error: {res.error_message}')

