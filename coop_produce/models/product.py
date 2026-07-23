from odoo import api, fields, models
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = "product.product"

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


class ProductTemplate(models.Model):
    _inherit = "product.template"

    default_packaging = fields.Float(
        default=1.0,
        digits="Product Price",
    )

    @api.constrains("default_packaging")
    def check_default_packaging(self):
        for product in self:
            if product.default_packaging <= 0.0:
                raise UserError(
                    self.env._(
                        "Default packaging of %s must be positive !",
                        product.name,
                    )
                )
