from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        params += ["barcode_base", "cooperative_state", "customer", "is_deceased"]
        return params

    @api.model
    def _load_pos_data_domain(self, data):
        """
        Load the domain for POS data, filtering out deceased partners.
        Important: Don't add the "customer" filter here, as it may exclude
        valid partners which caused issue in the POS such as
        "F#T67584 - [Internal] POS: Access rights" - Cashier cannot take money out
        """
        domain = super()._load_pos_data_domain(data)
        domain += [
            # ("customer", "=", True),
            ("is_deceased", "=", False),
        ]
        return domain
