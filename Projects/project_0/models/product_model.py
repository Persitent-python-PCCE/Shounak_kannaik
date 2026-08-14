class CreateProductRequest:
    def __init__(self, name: str, category_id: int, description: str, unit_price: float, stock_available: int):
        self.name = name
        self.category_id = category_id
        self.description = description
        self.unit_price = unit_price
        self.stock_available = stock_available

class CreateProductResponse:
    def __init__(self, product_id: int, error_message: str):
        self.product_id = product_id
        self.error_message = error_message

class ShowAllProductsResponse:
    def __init__(self, product_id: int, category_id: int, name: str, description: str,
                 unit_price: float, stock_available: int, created_at):
        self.product_id = product_id
        self.category_id = category_id
        self.name = name
        self.description = description
        self.unit_price = unit_price
        self.stock_available = stock_available
        self.created_at = created_at

class SearchProductRequest:
    def __init__(self, name: str):
        self.name = name

class SearchProductResponse:
    def __init__(self, product_id: int, category_id: int, name: str, description: str,
                 unit_price: float, stock_available: int, created_at, error_message: str):
        self.product_id = product_id
        self.category_id = category_id
        self.name = name
        self.description = description
        self.unit_price = unit_price
        self.stock_available = stock_available
        self.created_at = created_at
        self.error_message = error_message

class UpdateProductRequest:
    def __init__(self, product_id: int, name: str, category_id, description: str,
                 unit_price: str, stock_available: str):
        self.product_id = product_id
        self.name = name
        self.category_id = category_id
        self.description = description
        # These come in as strings from input(); blank means "no change"
        self.unit_price = unit_price
        self.stock_available = stock_available

class UpdateProductResponse:
    def __init__(self, affected_rows: int, error_message: str):
        self.affected_rows = affected_rows
        self.error_message = error_message

class DeleteProductRequest:
    def __init__(self, product_id: int):
        self.product_id = product_id

class DeleteProductResponse:
    def __init__(self, affected_rows: int, error_message: str):
        self.affected_rows = affected_rows
        self.error_message = error_message