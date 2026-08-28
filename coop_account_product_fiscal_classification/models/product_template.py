# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_expense_account_readonly = fields.Boolean(
        compute="_compute_is_account_readonly",
        help="Technical field",
    )
    is_income_account_readonly = fields.Boolean(
        compute="_compute_is_account_readonly",
        help="Technical field",
    )

    @api.model
    def get_fiscal_account(self, fc=False):
        vals = {}
        if fc and isinstance(fc, int):
            fc = self.env["account.product.fiscal.classification"].browse(fc)
        if not fc:
            return {
                "property_account_income_id": False,
                "property_account_expense_id": False,
            }
        if fc.income_account_id:
            vals.update({"property_account_income_id": fc.income_account_id.id})
        if fc.expense_account_id:
            vals.update({"property_account_expense_id": fc.expense_account_id.id})
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "fiscal_classification_id" in vals:
                fiscal_classification_id = vals.get("fiscal_classification_id")
                account_vals = self.get_fiscal_account(fiscal_classification_id)
                vals.update(account_vals)
        return super().create(vals)

    def write(self, vals):
        if "fiscal_classification_id" in vals:
            fiscal_classification_id = vals.get("fiscal_classification_id")
            account_vals = self.get_fiscal_account(fiscal_classification_id)
            vals.update(account_vals)
        return super().write(vals)

    @api.depends(
        "fiscal_classification_id.income_account_id",
        "fiscal_classification_id.expense_account_id",
    )
    def _compute_is_account_readonly(self):
        for rec in self:
            fc_id = rec.fiscal_classification_id
            rec.is_income_account_readonly = fc_id and fc_id.income_account_id
            rec.is_expense_account_readonly = fc_id and fc_id.expense_account_id
