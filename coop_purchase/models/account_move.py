from lxml import etree

from odoo import api, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            purchase_id = vals.get("purchase_id")
            if purchase_id:
                self.check_received_product(
                    self.env["purchase.order"].browse(purchase_id)
                )

        moves = super().create(vals_list)
        for move in moves:
            move._check_received_product_from_purchase_order()
        return moves

    def write(self, vals):
        purchase_id = vals.get("purchase_id")
        if purchase_id:
            self.check_received_product(self.env["purchase.order"].browse(purchase_id))

        res = super().write(vals)
        for move in self:
            move._check_received_product_from_purchase_order()
        return res

    def _check_received_product_from_purchase_order(self):
        self.ensure_one()
        if self.move_type not in ("in_invoice", "in_refund"):
            return

        purchase_orders = self.line_ids.purchase_line_id.order_id
        for purchase in purchase_orders:
            self.check_received_product(purchase)

    @api.onchange("purchase_vendor_bill_id", "purchase_id")
    def _onchange_purchase_auto_complete(self):
        if self.purchase_id:
            self.check_received_product(self.purchase_id)

        res = super()._onchange_purchase_auto_complete()

        for line in self.invoice_line_ids:
            suppliers = line.product_id.seller_ids.filtered(
                lambda x, partner_id=self.partner_id: x.partner_id == partner_id
            )
            if suppliers:
                line.base_price = suppliers[0].base_price

        return res

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        res = super().get_view(view_id=view_id, view_type=view_type, **options)

        account_advise = self.env.user.has_group("account.group_account_manager")
        if not account_advise and view_type == "form" and res.get("arch"):
            doc = etree.fromstring(res["arch"])
            list_readonly_field = [
                "journal_id",
                "user_id",
                "invoice_payment_term_id",
                "fiscal_position_id",
                "date",
                "company_id",
            ]
            for node in doc.xpath("//field"):
                if node.get("name") in list_readonly_field:
                    node.set("readonly", "1")
            res["arch"] = etree.tostring(doc, encoding="unicode")

        return res

    @api.model
    def check_received_product(self, purchase_id):
        pickings = purchase_id.picking_ids
        have_not_receive_picking = any(
            picking.state not in ["done", "cancel"] for picking in pickings
        )
        if have_not_receive_picking:
            raise UserError(
                self.env._(
                    "Please confirm reception before creating " "an invoice for this PO"
                )
            )

    def button_update_prices(self):
        self.ensure_one()
        return self.env["ir.actions.actions"]._for_xml_id(
            "coop_purchase.supplier_info_update_act"
        )
