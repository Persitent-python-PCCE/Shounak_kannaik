from DAO.category_dao import CategoryDAO
from models.category_model import (
    CreateCategoryRequest, CreateCategoryResponse,
    ShowAllCategoriesResponse,
    SearchCategoryRequest, SearchCategoryResponse,
    UpdateCategoryRequest, UpdateCategoryResponse,
    DeleteCategoryRequest, DeleteCategoryResponse,
    ViewCategoryProductsRequest
)

class CategoryService:
    def __init__(self):
        self.category_dao = CategoryDAO()

    def create_category(self, category: CreateCategoryRequest) -> CreateCategoryResponse:
        try:
            if category.name.strip() == "":
                raise ValueError("Category name cannot be empty")
        except ValueError as e:
            return CreateCategoryResponse(None, str(e))
        return self.category_dao.create_category(category=category)

    def show_all_categories(self) -> list:
        return self.category_dao.show_all_categories()

    def search_category(self, category: SearchCategoryRequest) -> SearchCategoryResponse:
        try:
            if category.name.strip() == "":
                raise ValueError("Category name cannot be empty")
        except ValueError as e:
            return SearchCategoryResponse(None, None, str(e))
        return self.category_dao.search_category(category=category)

    def update_category(self, category: UpdateCategoryRequest) -> UpdateCategoryResponse:
        try:
            if category.category_id is None:
                raise ValueError("category_id cannot be empty")
        except ValueError as e:
            return UpdateCategoryResponse(None, str(e))
        return self.category_dao.update_category(category=category)

    def delete_category(self, category: DeleteCategoryRequest) -> DeleteCategoryResponse:
        try:
            if category.category_id is None:
                raise ValueError("category_id cannot be empty")
        except ValueError as e:
            return DeleteCategoryResponse(None, str(e))
        return self.category_dao.delete_category(category=category)

    def view_category_products(self, category: ViewCategoryProductsRequest) -> list:
        try:
            if category.category_id is None:
                raise ValueError("category_id cannot be empty")
            return self.category_dao.view_category_products(category=category)
        except ValueError as e:
            raise e
