from odoo import http

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):
    @http.route(
        [
            """/shop""",
            """/shop/page/<int:page>""",
            """/shop/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>""",
            """/shop/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>/page/<int:page>""",
        ],
        type="http",
        auth="user",
        website=True,
    )
    def shop(self, page=0, category=None, search="", ppg=False, **post):
        res = super().shop(page, category, search, ppg, **post)
        return res

    @http.route(
        ['/shop/product/<model("product.template"):product>'],
        type="http",
        auth="user",
        website=True,
    )
    def product(self, product, category="", search="", **kwargs):
        res = super().product(product, category, search, **kwargs)
        return res
