from odoo import fields, models


class PurchaseConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    update_main_vendor_on_update_vendor_price = fields.Boolean(
        config_parameter="update_main_vendor_on_update_vendor_price",
    )
