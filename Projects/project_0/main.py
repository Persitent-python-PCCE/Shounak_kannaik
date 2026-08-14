from controller.user_controller import UserController
from controller.category_controller import CategoryController
from controller.product_controller import ProductController


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
                    user_menu()
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


def user_menu():
    while True:
        print("""
        ------------- EZ Buy -------------
        1. Products
        2. Categories
        3. Cart
        4. Orders
        0. Exit
        """)

        choice = input("Enter your choice: ")

        match choice:
            case "0":
                print("Exiting...")
                break

            case _:
                print("User menu coming soon...")


if __name__ == "__main__":
    main()