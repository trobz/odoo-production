from odoo import http

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleShopAccess(WebsiteSale):
    @http.route(
        [
            "/shop",
            "/shop/page/<int:page>",
            '/shop/category/<model("product.public.category"):category>',
            '/shop/category/<model("product.public.category"):category>/page/<int:page>',
        ],
        type="http",
        auth="user",
        website=True,
        sitemap=False,
    )
    def shop(
        self,
        page=0,
        category=None,
        search="",
        min_price=0.0,
        max_price=0.0,
        ppg=False,
        **post,
    ):
        return super().shop(
            page=page,
            category=category,
            search=search,
            min_price=min_price,
            max_price=max_price,
            ppg=ppg,
            **post,
        )

    @http.route(
        ['/shop/<model("product.template"):product>'],
        type="http",
        auth="user",
        website=True,
        sitemap=False,
        readonly=True,
    )
    def product(self, product, category="", search="", **kwargs):
        return super().product(product, category=category, search=search, **kwargs)
