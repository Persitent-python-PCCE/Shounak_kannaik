from controller.user_controller import UserController
from controller.category_controller import CategoryController
from controller.product_controller import ProductController
from controller.cart_controller import CartController
from controller.order_controller import OrderController


def main():
    user_controller = UserController()
    
    while True:
        print("""
        ------------- Welcome to EZ Buy -------------
        1. Login
        2. Create User
        0. Exit
        """)
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            current_user = user_controller.user_login()
            if current_user is not None:
                if current_user.role == "admin":
                    admin_menu(user_controller)
                else:
                    user_menu(current_user)
        elif choice == "2":
            user_controller.create_user()
        elif choice == "0":
            break
        else:
            print("Invalid choice. Please try again.")



def admin_menu(user_controller: UserController):
    category_controller = CategoryController()
    product_controller = ProductController()

    while True:
        print("""
            ------------- EZ Buy Admin -------------
            1. Users
            2. Products
            3. Categories
            4. Orders
            0. Exit
            """)

        choice = input("Enter your choice: ")

        match choice:
            case "1":
                while True:
                    print("""
                    ------------- Users -------------
                    1. View All Users
                    2. Search User
                    3. Update User
                    4. Delete User
                    0. Back
                    """)

                    user_choice = input("Enter your choice: ")

                    match user_choice:
                        case "1":
                            user_controller.show_all_users()

                        case "2":
                            user_controller.search_user()

                        case "3":
                            user_controller.update_user()

                        case "4":
                            user_controller.delete_user()

                        case "0":
                            break

                        case _:
                            print("Invalid choice")

            case "2":
                while True:
                    print("""
                    ------------- Products -------------
                    1. View All Products
                    2. Search Product
                    3. Add Product
                    4. Update Product
                    5. Delete Product
                    0. Back
                    """)

                    product_choice = input("Enter your choice: ")

                    match product_choice:
                        case "1":
                            product_controller.show_all_products()

                        case "2":
                            product_controller.search_product()

                        case "3":
                            product_controller.create_product()

                        case "4":
                            product_controller.update_product()

                        case "5":
                            product_controller.delete_product()

                        case "0":
                            break

                        case _:
                            print("Invalid choice")

            case "3":
                while True:
                    print("""
                    ------------- Categories -------------
                    1. View All Categories
                    2. View Category Products
                    3. Add Category
                    4. Update Category
                    5. Delete Category
                    0. Back
                    """)

                    category_choice = input("Enter your choice: ")

                    match category_choice:
                        case "1":
                            category_controller.show_all_categories()

                        case "2":
                            category_controller.view_category_products()

                        case "3":
                            category_controller.create_category()

                        case "4":
                            category_controller.update_category()

                        case "5":
                            category_controller.delete_category()

                        case "0":
                            break

                        case _:
                            print("Invalid choice")

            case "4":
                while True:
                    print("""
                    ------------- Orders -------------
                    1. View All Orders
                    2. Search Order
                    3. View Order Details
                    4. Update Order Status
                    5. Cancel Order
                    0. Back
                    """)

                    order_choice = input("Enter your choice: ")

                    match order_choice:
                        case "1":
                            print("View all orders")

                        case "2":
                            print("Search order")

                        case "3":
                            print("View order details")

                        case "4":
                            print("Update order status")

                        case "5":
                            print("Cancel order")

                        case "0":
                            break

                        case _:
                            print("Invalid choice")

            case "0":
                print("Exiting...")
                break

            case _:
                print("Invalid choice")


def browse_products_action(current_user, product_controller: ProductController, cart_controller: CartController, order_controller: OrderController, action: str):
    while True:
        name = input("Enter the exact product name (or 0 to cancel): ").strip()
        if name == "0":
            return

        product = product_controller.get_product_by_exact_name(name)
        if product is None:
            print(f"No product found with exact name '{name}'. Please try again.")
            continue

        while True:
            try:
                quantity = int(input(f"Enter quantity: ").strip())
                if quantity <= 0:
                    print("Quantity must be greater than zero. Try again.")
                    continue
                if quantity > product.stock_available:
                    print(f"Insufficient stock. Only {product.stock_available} available.")
                    return
                break
            except ValueError:
                print("Invalid input. Please enter a number.")

        if action == "buy":
            order_controller.direct_buy(current_user.user_id, product.product_id, quantity)
        elif action == "add_to_cart":
            cart_controller.add_to_cart(current_user.user_id, product.product_id, quantity)
        return


def user_menu(current_user):
    product_controller = ProductController()
    cart_controller = CartController()
    order_controller = OrderController()

    while True:
        print("""
        ------------- EZ Buy -------------
        1. Show Products
        2. Show Categories
        3. My Cart
        4. My Orders
        5. My Profile
        0. Logout
        """)

        choice = input("Enter your choice: ")

        match choice:
            case "1":
                products = product_controller.show_all_products()
                if not products:
                    continue

                print("""
        What would you like to do?
        1. Buy a product 
        2. Add product to cart
        0. Back
                """)
                sub = input("Enter your choice: ").strip().lower()

                if sub == "1":
                    browse_products_action(current_user, product_controller, cart_controller, order_controller, "buy")
                elif sub == "2":
                    browse_products_action(current_user, product_controller, cart_controller, order_controller, "add_to_cart")
                elif sub == "0":
                    continue
                else:
                    print("Invalid choice.")

            case "3":
                cart_controller.view_cart_menu(current_user.user_id)

            case "0":
                print("Logged out.")
                break

            case _:
                print("Coming soon...")


if __name__ == "__main__":
    main()