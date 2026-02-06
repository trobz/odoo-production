from odoo import models


class ResUsers(models.Model):
    _inherit = "res.users"

    def _load_pos_data(self, data):
        res = super()._load_pos_data(data)
        config = data["pos.config"]["data"][0]

        domain = self._load_pos_data_domain(data)
        user = self.search(domain, limit=1)
        user_groups = user.groups_id.ids

        res["data"][0].update(
            hasGroupPayment=config["group_payment_id"] in user_groups,
            hasGroupDiscount=config["group_discount_id"] in user_groups,
            hasGroupNegativeQty=config["group_negative_qty_id"] in user_groups,
            hasGroupPriceControl=config["group_change_unit_price_id"] in user_groups,
            hasGroupMultiOrder=config["group_multi_order_id"] in user_groups,
            hasGroupDeleteOrder=config["group_delete_order_id"] in user_groups,
        )
        return res
