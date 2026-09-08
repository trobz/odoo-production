from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def button_update_prices(self):
        self.ensure_one()
        return self.env["ir.actions.actions"]._for_xml_id(
            "coop_purchase.supplier_info_update_act"
        )

    def action_view_invoice(self, invoices=False):
        result = super().action_view_invoice(invoices)
        context = result.get("context")
        if isinstance(context, dict) and context.get("default_reference"):
            del context["default_reference"]
        return result

    picking_count = fields.Integer(compute_sudo=True)
    picking_ids = fields.Many2many(compute_sudo=True)
