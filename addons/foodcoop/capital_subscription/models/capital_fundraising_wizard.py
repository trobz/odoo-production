# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class CapitalFundraisingWizard(models.TransientModel):
    _name = "capital.fundraising.wizard"
    _description = "Capital Fundraising Wizard"

    def default_partner_id(self):
        if self._context.get("active_model", False) == "res.partner":
            return self._context.get("active_id", False)

    # Column Section
    date_invoice = fields.Date(string="Invoice Date", required=True)
    # TODO : uncoment this line when the membre registration will be done
    # in real time
    # default=fields.Date.context_today)

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True,
        default=default_partner_id,
    )

    fundraising_partner_type_ids = fields.Many2many(
        comodel_name="capital.fundraising.partner.type",
        string="Fundraising Partner Type",
        related="partner_id.fundraising_partner_type_ids",
    )

    share_qty = fields.Integer(string="Shares Quantity")

    category_id = fields.Many2one(
        comodel_name="capital.fundraising.category", string="Category", required=True
    )

    payment_journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Payment Method",
        domain="[('is_payment_capital_fundraising', '=', True)]",
    )

    confirm_fundraising_payment = fields.Selection(
        related="payment_journal_id.confirm_fundraising_payment"
    )

    confirm_payment = fields.Boolean(
        help="Check this box to confirm the"
        " payment(s). In that case, the second account move will be"
        " written to transfer amount from unpaid account to paid account",
    )

    payment_term_id = fields.Many2one(
        comodel_name="account.payment.term",
        string="Payment Term",
        domain="[('is_capital_fundraising', '=', True)]",
        required=True,
    )

    # On change section
    @api.onchange("partner_id", "category_id")
    def onchange_partner_category(self):
        if self.partner_id and self.category_id:
            to_order_qty = self.category_id.check_minimum_qty(self.partner_id)
            self.share_qty = max(1, to_order_qty)

    @api.onchange("payment_journal_id")
    def onchange_payment_journal_id(self):
        if self.payment_journal_id:
            self.confirm_payment = self.confirm_fundraising_payment in [
                "allways",
                "yes",
            ]
        else:
            self.confirm_payment = False

    # Action Section
    def button_confirm(self):
        self.ensure_one()
        invoice_obj = self.env["account.move"]
        wizard = self[0]
        product = wizard.category_id.product_id
        invoice_vals = invoice_obj.default_get(invoice_obj._fields.keys())
        invoice_vals.update(
            {
                "move_type": "out_invoice",
                "invoice_date": wizard.date_invoice,
                "journal_id": wizard.category_id.fundraising_id.journal_id.id,
                "invoice_payment_term_id": wizard.payment_term_id.id,
                "partner_id": wizard.partner_id.id,
                "is_capital_fundraising": True,
                "fundraising_category_id": wizard.category_id.id,
                "invoice_line_ids": [
                    [
                        0,
                        False,
                        {
                            "product_uom_id": product.uom_id.id,
                            "product_id": product.id,
                            "price_unit": product.lst_price,
                            "name": product.name,
                            "quantity": wizard.share_qty,
                            "account_id": product.property_account_income_id.id,
                        },
                    ]
                ],
            }
        )

        # Create new invoice
        invoice = invoice_obj.create(invoice_vals)
        invoice.onchange_fundraising_category_id()

        # Validate Invoice
        invoice.action_post()

        # Mark Payment
        if wizard.payment_journal_id:
            # Force confirm_payment is True in case
            # Confirm Fundraising Payments is always
            if wizard.confirm_fundraising_payment in ["allways"]:
                wizard.confirm_payment = True
            if wizard.confirm_payment:
                payment_vals = {
                    "journal_id": wizard.payment_journal_id.id,
                    "payment_date": wizard.date_invoice,
                }
                payment_register = (
                    self.env["account.payment.register"]
                    .with_context(active_model="account.move", active_ids=invoice.ids)
                    .create(payment_vals)
                )
                payment_register._create_payments()

        # Return view on the new invoice
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_move_out_invoice_type"
        )
        form_view_id = self.env.ref("account.view_move_form").id
        action.update(
            {
                "views": [(form_view_id, "form")],
                "view_mode": "form",
                "res_id": invoice.id,
            }
        )
        return action
