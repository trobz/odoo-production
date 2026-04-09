from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

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
        return super(ProductProduct, self).search(domain, *args, **kwargs)  # noqa: UP008

    def toggle_active(self):
        res = super().toggle_active()
        for variant in self:
            if variant.active:
                if not variant.product_tmpl_id.active:
                    variant.product_tmpl_id.active = True
            elif variant.product_tmpl_id.active:
                other_variants = variant.product_tmpl_id.mapped(
                    "product_variant_ids"
                ).filtered(lambda v: v.active)
                if not other_variants:
                    variant.product_tmpl_id.active = False
        return res
