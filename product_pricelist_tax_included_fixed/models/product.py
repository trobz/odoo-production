# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    list_price_tax = fields.Float(
        string="Sale price with taxes",
        digits="Product Price",
    )

    def _extract_tax_ids(self, commands):
        """Extract tax IDs from a plain int list or ORM command list."""
        tax_ids = []
        for cmd in commands:
            if isinstance(cmd, int):  # plain id
                tax_ids.append(cmd)
            elif cmd[0] == 6 and len(cmd) >= 3:  # SET
                tax_ids = list(cmd[2])
            elif cmd[0] == 4 and len(cmd) >= 2:  # LINK
                tax_ids.append(cmd[1])
        return tax_ids

    def _get_factor_tax(self, taxes):
        if not taxes:
            return 1.0
        if not isinstance(taxes, models.BaseModel):
            taxes = self.env["account.tax"].browse(self._extract_tax_ids(taxes))
        tax_percent = sum([tax.amount for tax in taxes if not tax.price_include])
        factor_tax = (1 + tax_percent / 100) or 1.0
        return factor_tax

    def _resolve_taxes_commands(self, commands):
        """Apply ORM commands to current taxes and return resulting recordset."""
        tax_ids = set(self.taxes_id.ids)
        for cmd in commands:
            if isinstance(cmd, int):  # plain id
                tax_ids.add(cmd)
            elif cmd[0] == 6 and len(cmd) >= 3:  # SET
                tax_ids = set(cmd[2])
            elif cmd[0] == 4 and len(cmd) >= 2:  # LINK
                tax_ids.add(cmd[1])
            elif cmd[0] == 3 and len(cmd) >= 2:  # UNLINK
                tax_ids.discard(cmd[1])
            elif cmd[0] == 2 and len(cmd) >= 2:  # DELETE
                tax_ids.discard(cmd[1])
            elif cmd[0] == 5:  # CLEAR
                tax_ids = set()
        return self.env["account.tax"].browse(list(tax_ids))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            list_price_tax = float(vals.get("list_price_tax", 0.0))
            list_price = float(vals.get("list_price", 0.0))
            taxes_id = vals.get("taxes_id")
            if list_price_tax != 0.0:
                amount_tax = list_price_tax - (
                    list_price_tax / self._get_factor_tax(taxes_id)
                )
                vals["list_price"] = list_price_tax - amount_tax
            else:
                vals["list_price_tax"] = list_price * self._get_factor_tax(taxes_id)
        return super().create(vals_list)

    def write(self, vals):
        if not ("list_price_tax" in vals or "list_price" in vals or "taxes_id" in vals):
            return super().write(vals)
        for product in self:
            product_vals = vals.copy()
            raw_taxes = product_vals.get("taxes_id")
            if raw_taxes and not isinstance(raw_taxes, models.BaseModel):
                taxes_id = product._resolve_taxes_commands(raw_taxes)
            else:
                taxes_id = raw_taxes or product.taxes_id
            if "list_price_tax" in product_vals:
                list_price_tax = float(product_vals.get("list_price_tax", 0.0))
                factor_tax = product._get_factor_tax(taxes_id)
                amount_tax = list_price_tax - (list_price_tax / factor_tax)
                product_vals["list_price"] = list_price_tax - amount_tax
            else:
                list_price = product.list_price
                if "list_price" in product_vals:
                    list_price = float(product_vals["list_price"])
                product_vals["list_price_tax"] = list_price * product._get_factor_tax(
                    taxes_id
                )
            super(ProductTemplate, product).write(product_vals)
        return True
