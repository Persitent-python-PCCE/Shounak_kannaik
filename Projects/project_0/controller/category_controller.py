from service.category_service import CategoryService
from models.category_model import (
    CreateCategoryRequest,
    SearchCategoryRequest,
    UpdateCategoryRequest,
    DeleteCategoryRequest,
    ViewCategoryProductsRequest
)

class CategoryController:
    def __init__(self):
        self.category_service = CategoryService()

    def create_category(self):
        name = input("Enter category name: ").strip()
        category = CreateCategoryRequest(name=name)
        response_obj = self.category_service.create_category(category)
        if response_obj.error_message is None:
            print(f"Category created successfully! category_id: {response_obj.category_id}")
        else:
            print(f"Error: {response_obj.error_message}")

    def show_all_categories(self) -> list:
        categories = self.category_service.show_all_categories()
        if categories:
            print(f"\n------------- All Categories: total: {len(categories)} -------------")
            for i, cat in enumerate(categories):
                print(f"  {i + 1}. category_id: {cat.category_id}\tname: {cat.name}")
        else:
            print("No categories found.")
        return categories

    def search_category(self):
        name = input("Enter category name to search: ").strip()
        category = SearchCategoryRequest(name=name)
        response_obj = self.category_service.search_category(category)
        if response_obj.error_message is None:
            print(f"\nCategory found!")
            print(f"  category_id: {response_obj.category_id}\tname: {response_obj.name}")
        else:
            print(f"Error: {response_obj.error_message}")

    def update_category(self):
        self.show_all_categories()
        category_id = int(input("Enter the category_id to update: "))
        print("Enter the new details (leave blank to keep current value):")
        name = input("Update Name: ").strip()
        category = UpdateCategoryRequest(category_id=category_id, name=name)
        response_obj = self.category_service.update_category(category)
        if response_obj.affected_rows is not None and response_obj.error_message is None:
            print("Category updated successfully.")
        else:
            print(f"Error: {response_obj.error_message}")

    def delete_category(self):
        self.show_all_categories()
        category_id = int(input("Enter the category_id to delete: "))
        confirm = input(f"Are you sure you want to delete category with category_id {category_id}? (yes/no): ")
        if confirm.lower() != "yes":
            print("Delete cancelled.")
            return
        category = DeleteCategoryRequest(category_id=category_id)
        response_obj = self.category_service.delete_category(category)
        if response_obj.affected_rows is not None and response_obj.error_message is None:
            print(f"Category with category_id {category_id} deleted successfully.")
        else:
            print(f"Error: {response_obj.error_message}")

    def view_category_products(self):
        self.show_all_categories()
        category_id = int(input("Enter the category_id to view its products: "))
        category = ViewCategoryProductsRequest(category_id=category_id)
        try:
            products = self.category_service.view_category_products(category)
            if products:
                print(f"\n------------- Products in category_id {category_id}: total: {len(products)} -------------")
                for i, p in enumerate(products):
                    print(f"  {i + 1}. product_id: {p[0]}\tname: {p[1]}\tprice: {p[3]}\tstock: {p[4]}")
                    if p[2]:
                        print(f"       description: {p[2]}")
            else:
                print("No products found in this category.")
        except ValueError as e:
            print(f"Error: {e}")
