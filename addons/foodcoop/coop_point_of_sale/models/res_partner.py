from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        params += ["barcode_base", "cooperative_state"]
        return params

    @api.model
    def _load_pos_data_domain(self, data):
        domain = super()._load_pos_data_domain(data)
        domain += [
            ("customer_rank", ">=", 1),
            ("is_deceased", "=", False),
        ]
        return domain
