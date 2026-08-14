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