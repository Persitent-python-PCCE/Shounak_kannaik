from DAO.product_dao import ProductDAO
from models.product_model import (
    CreateProductRequest, CreateProductResponse,
    ShowAllProductsResponse,
    SearchProductRequest, SearchProductResponse,
    UpdateProductRequest, UpdateProductResponse,
    DeleteProductRequest, DeleteProductResponse
)

class ProductService:
    def __init__(self):
        self.product_dao = ProductDAO()

    def create_product(self, product: CreateProductRequest) -> CreateProductResponse:
        try:
            if product.name.strip() == "":
                raise ValueError("Product name cannot be empty")
            if product.unit_price < 0:
                raise ValueError("Unit price cannot be negative")
            if product.stock_available < 0:
                raise ValueError("Stock available cannot be negative")
            if product.category_id is None or product.category_id == "":
                raise ValueError("category_id cannot be empty")
        except ValueError as e:
            return CreateProductResponse(None, str(e))
        return self.product_dao.create_product(product=product)

    def show_all_products(self) -> list:
        return self.product_dao.show_all_products()

    def search_product(self, product: SearchProductRequest) -> list:
        try:
            if product.name.strip() == "":
                raise ValueError("Product name to search cannot be empty")
            return self.product_dao.search_product(product=product)
        except ValueError as e:
            raise e

    def update_product(self, product: UpdateProductRequest) -> UpdateProductResponse:
        try:
            if product.product_id is None:
                raise ValueError("product_id cannot be empty")
            # Validate numeric fields only if they are being updated
            if product.unit_price.strip() != "":
                price = float(product.unit_price)
                if price < 0:
                    raise ValueError("Unit price cannot be negative")
            if product.stock_available.strip() != "":
                stock = int(product.stock_available)
                if stock < 0:
                    raise ValueError("Stock available cannot be negative")
        except ValueError as e:
            return UpdateProductResponse(None, str(e))
        return self.product_dao.update_product(product=product)

    def delete_product(self, product: DeleteProductRequest) -> DeleteProductResponse:
        try:
            if product.product_id is None:
                raise ValueError("product_id cannot be empty")
        except ValueError as e:
            return DeleteProductResponse(None, str(e))
        return self.product_dao.delete_product(product=product)
