from flask import Blueprint, jsonify

from src.application.requests.products.get_products import GetProducts

# TODO: set url_prefix to products
products_blueprint = Blueprint('products', __name__, url_prefix="")


@products_blueprint.route("/", methods=["GET"])
def get_products():
    get_products_response = GetProducts.handle()

    return jsonify(get_products_response)
