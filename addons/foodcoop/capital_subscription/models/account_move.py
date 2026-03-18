# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from ast import literal_eval

from odoo import api, exceptions, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    # Column Section
    is_capital_fundraising = fields.Boolean(string="Concerns Capital Fundraising")

    fundraising_category_id = fields.Many2one(
        comodel_name="capital.fundraising.category", string="Fundraising Category"
    )

    # Constraint Section
    @api.constrains(
        "is_capital_fundraising",
        "fundraising_category_id",
        "partner_id",
        "invoice_line_ids",
        "state",
        "move_type",
        "payment_state",
    )
    def _check_capital_fundraising(self):
        for invoice in self:
            if invoice.move_type not in ["out_invoice", "out_refund"]:
                continue
            product_ids = invoice.invoice_line_ids.filtered(
                lambda line: line.display_type == "product"
            ).mapped("product_id.id")

            if invoice.is_capital_fundraising:
                # Check mandatory field
                if not invoice.fundraising_category_id:
                    raise exceptions.UserError(
                        self.env._(
                            "A Capital fundraising must have a capital category defined"
                        )
                    )

                # Check products
                forbidden_product_ids = list(
                    set(product_ids)
                    - set([invoice.fundraising_category_id.product_id.id])
                )
                if forbidden_product_ids:
                    forbidden_products = self.env["product.product"].browse(
                        forbidden_product_ids
                    )
                    if not all(
                        [
                            each_prod.is_deficit_product
                            for each_prod in forbidden_products
                        ]
                    ):
                        raise exceptions.UserError(
                            self.env._(
                                "%(category)s category do not allow "
                                "%(products)s products"
                            )
                            % {
                                "category": invoice.fundraising_category_id.name,
                                "products": ", ".join(
                                    forbidden_products.mapped("name")
                                ),
                            }
                        )

            else:
                capital_product_ids = (
                    self.env["product.product"]
                    .search([("is_capital_fundraising", "=", True)])
                    .ids
                )
                forbidden_product_ids = list(
                    set(product_ids).intersection(capital_product_ids)
                )
                if forbidden_product_ids:
                    forbidden_product_names = ", ".join(
                        self.env["product.product"]
                        .browse(forbidden_product_ids)
                        .mapped("name")
                    )
                    raise exceptions.UserError(
                        self.env._(
                            "Non capital invoice do not accept line with capital"
                            " subscription products : %s"
                        )
                        % (forbidden_product_names)
                    )

            if invoice.state == "posted" and invoice.fundraising_category_id:
                category = invoice.fundraising_category_id
                # Get default minimum qty
                minimum_qty = category.minimum_share_qty

                # Compute minimum qty depending of partner state
                if invoice.partner_id.fundraising_partner_type_ids:
                    for line in category.line_ids:
                        if (
                            line.fundraising_partner_type_id.id
                            in invoice.partner_id.fundraising_partner_type_ids.ids
                        ):
                            minimum_qty = min(line.minimum_share_qty, minimum_qty)

                capital_qty = 0
                category_invoices = self.search(
                    [
                        ("partner_id", "=", invoice.partner_id.id),
                        ("state", "=", "posted"),
                        ("move_type", "in", ["out_invoice", "out_refund"]),
                        ("fundraising_category_id", "=", category.id),
                    ]
                )
                for category_invoice in category_invoices:
                    qty = sum(
                        [
                            inv_line.quantity
                            for inv_line in category_invoice.invoice_line_ids
                            if inv_line.product_id
                            and inv_line.product_id.is_capital_fundraising
                        ]
                    )
                    if category_invoice.move_type == "out_invoice":
                        capital_qty += qty
                    else:
                        capital_qty -= qty

                if capital_qty < 0:
                    raise exceptions.UserError(
                        self.env._(
                            "You try to make an operation after which the partner"
                            " will have %(qty)s shares of capital of kind "
                            "'%(category)s'.\n\n"
                            " Incorrect Value."
                        )
                        % {
                            "qty": capital_qty,
                            "category": category.name,
                        }
                    )
                if (
                    capital_qty < minimum_qty
                    and capital_qty != 0
                    and not self.env.context.get("ignore_type_A_constrains", False)
                ):
                    # use this test to ignore type A constrains when
                    # partial transfer capital will be implemented. IE :
                    # Partner bought 10 shares
                    # Partner gives 5 shares to another member (*)
                    # (5 shares left)
                    # Partner ask refund for the other shares (0 shares left)
                    # (*) : this invoice confirmation should be accepted,
                    # even if the partner has 5 shares during this step.
                    raise exceptions.UserError(
                        self.env._(
                            "You try to make an operation after which the partner"
                            " will have %(qty)s share(s) of capital of kind "
                            "'%(category)s'.\n\n"
                            " Minimum quantity : %(minimum_qty)s."
                        )
                        % {
                            "qty": capital_qty,
                            "category": category.name,
                            "minimum_qty": minimum_qty,
                        }
                    )

    # OnChange Section
    @api.onchange("fundraising_category_id")
    def onchange_fundraising_category_id(self):
        if self.fundraising_category_id:
            self.journal_id = self.fundraising_category_id.fundraising_id.journal_id

    def apply_refund_deficit_share(self, quantity=0):
        """
        @Function to apply the deficit share on customer refund
        """

        for invoice in self:
            fundraising_categ = invoice.fundraising_category_id
            if (
                invoice.move_type == "out_refund"
                and fundraising_categ
                and quantity >= 0
            ):
                deficit_share_amount = fundraising_categ.get_deficit_share_amount(
                    invoice.invoice_date or fields.Date.context_today(self)
                )

                for inv_line in invoice.invoice_line_ids:
                    source_product = inv_line.product_id
                    if source_product and source_product.is_capital_fundraising:
                        if (
                            not source_product.deficit_share_account_id
                            and deficit_share_amount
                        ):
                            raise UserError(
                                self.env._(
                                    "Deficit Share Account has not "
                                    "been configured for %s."
                                )
                                % source_product.display_name
                            )
                        # Update quantity of source product line
                        inv_line.write({"quantity": quantity})

                        if deficit_share_amount:
                            # Adjust the Unit Price of the line
                            deficit_price_unit_signed = -1.0 * deficit_share_amount

                            if fundraising_categ.capital_account_id:
                                inv_line.account_id = (
                                    fundraising_categ.capital_account_id.id
                                )

                            # Create a new line
                            deficit_share_prod = fundraising_categ.deficit_product_id

                            deficit_line_val = {
                                "product_id": deficit_share_prod
                                and deficit_share_prod.id
                                or False,
                                "name": deficit_share_prod
                                and deficit_share_prod.display_name
                                or self.env._("Deficit Share"),
                                "account_id": (
                                    source_product.deficit_share_account_id.id
                                ),
                                "quantity": quantity,
                                "price_unit": deficit_price_unit_signed,
                                "product_uom_id": inv_line.product_uom_id
                                and inv_line.product_uom_id.id
                                or False,
                                "move_id": invoice.id,
                            }

                            self.env["account.move.line"].create(deficit_line_val)

                            # break because the quantity is total shares
                            # and we don't have different capital fundraising
                            # products in one invoice, therefore break when
                            # we get the first one satisfy and update with
                            # total quantity.
                            break

    def action_reverse(self):
        # Override to set the context for the reversal reason
        action = super().action_reverse()
        invoices = self.filtered("is_capital_fundraising")
        if invoices:
            invoice = invoices[0]
            reason = self.env._("Redemption %(move)s - %(barcode)s") % {
                "move": invoice.name,
                "barcode": invoice.partner_id.barcode_base,
            }
            qty = sum(
                [
                    line.quantity
                    for line in invoices.mapped("invoice_line_ids")
                    if line.product_id.is_capital_fundraising
                ]
            )
            action["context"] = dict(
                literal_eval(action.get("context", "{}")),
                default_reason=reason,
                default_refund_quantity=qty,
                default_refund_quantity_origin=qty,
            )
        return action
