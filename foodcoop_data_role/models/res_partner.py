from lxml import etree

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        res = super().get_view(view_id=view_id, view_type=view_type, **options)
        if view_type == "form" and self.env.user.has_groups(
            "foodcoop_data_role.group_Purchaser,"
            "!foodcoop_data_role.group_Foodcoop_Admin,"
            "!base.group_system"
        ):
            doc = etree.XML(res["arch"])
            doc.set("edit", "false")
            doc.set("create", "false")
            res["arch"] = etree.tostring(doc, encoding="unicode")
        return res
