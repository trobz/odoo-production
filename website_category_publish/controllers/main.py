from odoo import http
from odoo.osv import expression

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteCategoryPublish(WebsiteSale):
    """Overwrite this controller to support category published filters"""

    def _get_shop_domain(
        self, search, category, attrib_values, search_in_description=True
    ):
        domain = super()._get_shop_domain(
            search, category, attrib_values, search_in_description
        )
        args = [("is_categ_published", "=", True)]
        domain = expression.AND([args, domain])
        return domain

    @http.route()
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
        response = super().shop(
            page=page,
            category=category,
            search=search,
            min_price=min_price,
            max_price=max_price,
            ppg=ppg,
            **post,
        )

        if "categories" in response.qcontext:
            categories = response.qcontext["categories"]
            response.qcontext["categories"] = categories.filtered(
                lambda c: c.is_published
            )
        return response
