class CreateCategoryRequest:
    def __init__(self, name: str):
        self.name = name

class CreateCategoryResponse:
    def __init__(self, category_id: int, error_message: str):
        self.category_id = category_id
        self.error_message = error_message

class ShowAllCategoriesResponse:
    def __init__(self, category_id: int, name: str):
        self.category_id = category_id
        self.name = name

class SearchCategoryRequest:
    def __init__(self, name: str):
        self.name = name

class SearchCategoryResponse:
    def __init__(self, category_id: int, name: str, error_message: str):
        self.category_id = category_id
        self.name = name
        self.error_message = error_message

class UpdateCategoryRequest:
    def __init__(self, category_id: int, name: str):
        self.category_id = category_id
        self.name = name

class UpdateCategoryResponse:
    def __init__(self, affected_rows: int, error_message: str):
        self.affected_rows = affected_rows
        self.error_message = error_message

class DeleteCategoryRequest:
    def __init__(self, category_id: int):
        self.category_id = category_id

class DeleteCategoryResponse:
    def __init__(self, affected_rows: int, error_message: str):
        self.affected_rows = affected_rows
        self.error_message = error_message

class ViewCategoryProductsRequest:
    def __init__(self, category_id: int):
        self.category_id = category_id


# --- User-facing: browse products by category name ---
class ShowCategoryProductsByNameRequest:
    def __init__(self, category_name: str):
        self.category_name = category_name

class CategoryProductModel:
    def __init__(self, product_id: int, name: str, unit_price: float, stock_available: int):
        self.product_id = product_id
        self.name = name
        self.unit_price = unit_price
        self.stock_available = stock_available

class ShowCategoryProductsByNameResponse:
    def __init__(self, category_name: str, items: list, error_message: str = None):
        self.category_name = category_name
        self.items = items          # list of CategoryProductModel
        self.error_message = error_message