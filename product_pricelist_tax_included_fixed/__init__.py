from . import models


def post_init_hook(env):
    """Update list price with taxes include for all products."""
    products = env["product.template"].search([])
    for product in products:
        product.list_price_tax = product.list_price * product._get_factor_tax(
            product.taxes_id
        )
