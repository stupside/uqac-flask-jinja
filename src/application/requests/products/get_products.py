from src.domain.models import Product


class GetProducts:

    @staticmethod
    def handle():
        return {
            "products": list(Product.select(Product.id,
                                            Product.name,
                                            Product.in_stock,
                                            Product.description,
                                            Product.price,
                                            Product.weight,
                                            Product.image).dicts())
        }
