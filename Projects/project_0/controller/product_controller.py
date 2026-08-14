from service.product_service import ProductService
from models.product_model import (
    CreateProductRequest,
    SearchProductRequest,
    UpdateProductRequest,
    DeleteProductRequest
)

class ProductController:
    def __init__(self):
        self.product_service = ProductService()

    def _print_product(self, index: int, p):
        print(f"  {index}. product_id: {p.product_id}\t| category: {p.category}\t| name: {p.name}"
              f"\t| price: {p.unit_price}\t| stock: {p.stock_available}")

    def create_product(self):
        print("\n--- Add New Product ---")
        name = input("Enter product name: ")
        category_id_str = input("Enter category_id: ")
        description = input("Enter description (optional): ")
        unit_price_str = input("Enter unit price: ")
        stock_str = input("Enter stock available: ")

        try:
            category_id = int(category_id_str) if category_id_str != "" else None
            unit_price = float(unit_price_str)
            stock_available = int(stock_str)
        except ValueError:
            print("Error: Invalid numeric value entered for category_id, price, or stock.")
            return

        product = CreateProductRequest(
            name=name, category_id=category_id, description=description,
            unit_price=unit_price, stock_available=stock_available
        )
        response_obj = self.product_service.create_product(product)
        if response_obj.error_message is None:
            print(f"Product created successfully! product_id: {response_obj.product_id}")
        else:
            print(f"Error: {response_obj.error_message}")

    def show_all_products(self) -> list:
        products = self.product_service.show_all_products()
        if products:
            print(f"\n------------- All Products: total: {len(products)} -------------")
            for i, p in enumerate(products):
                self._print_product(i + 1, p)
        else:
            print("No products found.")
        return products

    def get_product_by_exact_name(self, name: str):
        try:
            results = self.product_service.search_product(SearchProductRequest(name=name))
            exact = [p for p in results if p.name.strip().lower() == name.strip().lower()]
            if len(exact) == 1:
                return exact[0]
            return None
        except ValueError:
            return None

    def search_product(self):
        name = input("Enter product name to search: ").strip()
        product = SearchProductRequest(name=name)
        try:
            results = self.product_service.search_product(product)
            if results:
                print(f"\n--- Search Results: {len(results)} found ---")
                for i, p in enumerate(results):
                    self._print_product(i + 1, p)
                    if p.description:
                        print(f"       description: {p.description}")
            else:
                print(f"No products found matching '{name}'.")
        except ValueError as e:
            print(f"Error: {e}")

    def update_product(self):
        self.show_all_products()
        try:
            product_id = int(input("Enter the product_id to update: "))
        except ValueError:
            print("Invalid product_id.")
            pause()
            return
        print("Enter the new details (leave blank to keep current value):")
        name = input("Update Name: ")
        category_id = input("Update category_id: ").strip()
        description = input("Update Description: ")
        unit_price = input("Update Unit Price: ")
        stock_available = input("Update Stock Available: ")

        product = UpdateProductRequest(
            product_id=product_id,
            name=name,
            category_id=int(category_id) if category_id != "" else "",
            description=description,
            unit_price=unit_price,
            stock_available=stock_available
        )
        response_obj = self.product_service.update_product(product)
        if response_obj.affected_rows is not None and response_obj.error_message is None:
            print("Product updated successfully.")
        else:
            print(f"Error: {response_obj.error_message}")

    def delete_product(self):
        self.show_all_products()
        try:
            product_id = int(input("Enter the product_id to delete: "))
        except ValueError:
            print("Invalid product_id.")
            pause()
            return
        confirm = input(f"Are you sure you want to delete product with product_id {product_id}? (y/n): ")
        if confirm.lower() != "y":
            print("Delete cancelled.")
            return
        product = DeleteProductRequest(product_id=product_id)
        response_obj = self.product_service.delete_product(product)
        if response_obj.affected_rows is not None and response_obj.error_message is None:
            print(f"Product with product_id {product_id} deleted successfully.")
        else:
            print(f"Error: {response_obj.error_message}")
