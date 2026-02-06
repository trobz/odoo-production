from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    group_negative_qty_id = fields.Many2one(
        comodel_name="res.groups",
        string="Point of Sale - Allow Negative Quantity",
        compute="_compute_groups",
        help="This field is there to pass the id of the 'PoS - Allow Negative"
        " Quantity' Group to the Point of Sale Frontend.",
    )

    group_discount_id = fields.Many2one(
        comodel_name="res.groups",
        string="Point of Sale - Allow Discount",
        compute="_compute_groups",
        help="This field is there to pass the id of the 'PoS - Allow Discount'"
        " Group to the Point of Sale Frontend.",
    )

    group_change_unit_price_id = fields.Many2one(
        comodel_name="res.groups",
        string="Point of Sale - Allow Unit Price Change",
        compute="_compute_groups",
        help="This field is there to pass the id of the 'PoS - Allow Unit"
        " Price Change' Group to the Point of Sale Frontend.",
    )

    group_multi_order_id = fields.Many2one(
        comodel_name="res.groups",
        string="Point of Sale - Many Orders",
        compute="_compute_groups",
        help="This field is there to pass the id of the 'PoS - Many Orders"
        " Group to the Point of Sale Frontend.",
    )

    group_delete_order_id = fields.Many2one(
        comodel_name="res.groups",
        string="Point of Sale - Delete Order",
        compute="_compute_groups",
        help="This field is there to pass the id of the 'PoS - Delete Order'"
        " Group to the Point of Sale Frontend.",
    )

    group_payment_id = fields.Many2one(
        comodel_name="res.groups",
        string="Point of Sale - Payment",
        compute="_compute_groups",
        help="This field is there to pass the id of the 'PoS - Payment'"
        " Group to the Point of Sale Frontend.",
    )

    def _compute_groups(self):
        group_negative_qty = self.env.ref("pos_access_right.group_negative_qty")
        group_discount = self.env.ref("pos_access_right.group_discount")
        group_change_unit_price = self.env.ref(
            "pos_access_right.group_change_unit_price"
        )
        group_multi_order = self.env.ref("pos_access_right.group_multi_order")
        group_delete_order = self.env.ref("pos_access_right.group_delete_order")
        group_payment = self.env.ref("pos_access_right.group_payment")
        for config in self:
            config.group_negative_qty_id = group_negative_qty.id
            config.group_discount_id = group_discount
            config.group_change_unit_price_id = group_change_unit_price.id
            config.group_multi_order_id = group_multi_order.id
            config.group_delete_order_id = group_delete_order.id
            config.group_payment_id = group_payment.id
