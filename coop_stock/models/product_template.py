from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def search(self, domain, *args, **kwargs):
        allow_inactive_search_fields = ["barcode"]
        not_allow_inactive = ["name"]
        allow_inactive_search_field_domain = filter(
            lambda arg: isinstance(arg, list | tuple)
            and arg[0] in allow_inactive_search_fields,
            domain,
        )
        not_allow_inactive_domain = filter(
            lambda arg: isinstance(arg, list | tuple) and arg[0] in not_allow_inactive,
            domain,
        )
        if not list(not_allow_inactive_domain) and list(
            allow_inactive_search_field_domain
        ):
            self = self.with_context(active_test=False)
        return super(ProductTemplate, self).search(domain, *args, **kwargs)  # noqa: UP008
