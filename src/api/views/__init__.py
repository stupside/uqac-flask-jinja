# TODO: set url_prefix to /api

from flask import Blueprint, render_template

from src.application.requests.products.get_products import GetProducts

api_blueprint = Blueprint('api', __name__, template_folder="../templates", static_folder="static", url_prefix="/")


@api_blueprint.route("/products")
def products():
    get_products_response = GetProducts.handle()

    return render_template("products.html", products=get_products_response["products"])
