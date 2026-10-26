from odoo import fields, models


class ProductPrintWizardLine(models.TransientModel):
    _inherit = "product.print.wizard.line"

    print_category_id = fields.Many2one(readonly=True)
