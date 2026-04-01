from odoo import api, fields, models
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = "product.product"

    default_packaging = fields.Float(
        compute="_compute_default_packaging",
        store=True,
        digits="Product Price",
    )

    @api.constrains("barcode")
    def _check_barcode_uniq(self):
        for product in self:
            if not product.barcode:
                continue
            one = self.search(
                [("barcode", "=", product.barcode), ("id", "!=", product.id)], limit=1
            )
            if one:
                raise UserError(
                    self.env._(
                        "Barcode '%s' has been assigned to the product '%s'!",
                        product.barcode,
                        one.name,
                    )
                ) from None

    @api.depends("name")
    @api.depends_context("order_planning_context")
    def _compute_display_name(self):
        """Return the product name without ref when the
        name_get is called from order planning form
        """
        if not self.env.context.get("order_planning_context"):
            return super()._compute_display_name()
        else:
            for record in self:
                record.display_name = record.name

    @api.depends("packaging_ids", "packaging_ids.qty", "packaging_ids.sequence")
    def _compute_default_packaging(self):
        for product in self:
            default_packaging = product.packaging_ids.sorted(
                key=lambda packaging: (packaging.sequence, packaging.id)
            )[:1].qty
            product.default_packaging = default_packaging or 0.0


class ProductTemplate(models.Model):
    _inherit = "product.template"

    default_packaging = fields.Float(
        compute="_compute_default_packaging",
        store=True,
        digits="Product Price",
    )

    @api.depends(
        "product_variant_ids",
        "product_variant_ids.default_packaging",
    )
    def _compute_default_packaging(self):
        for product in self:
            product.default_packaging = product.product_variant_id.default_packaging
