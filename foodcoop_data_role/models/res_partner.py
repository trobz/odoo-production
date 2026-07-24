from lxml import etree

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def get_views(self, views, options=None):
        res = super().get_views(views, options)
        if self.env.user.has_groups(
            "foodcoop_data_role.group_Purchaser,"
            "!foodcoop_data_role.group_Foodcoop_Admin,"
            "!base.group_system,"
            "foodcoop_data_role.group_POS_Manager,"
            "foodcoop_data_role.group_Cashier"
        ):
            for _view_type, view_data in res.get("views", {}).items():
                doc = etree.XML(view_data["arch"])
                doc.set("edit", "false")
                doc.set("create", "false")
                doc.set("delete", "false")
                view_data["arch"] = etree.tostring(doc, encoding="unicode")
                view_data["toolbar"] = {}
        return res
