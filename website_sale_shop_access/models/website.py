from odoo import models
from odoo.http import request


class Page(models.Model):
    _inherit = "website.page"

    def _compute_visible(self):
        res = super()._compute_visible()
        for page in self:
            if (
                page.is_visible
                and request
                and page.view_id.visibility == "restricted_group"
                and page.groups_id
            ):
                user_groups = set(request.env.user.groups_id)
                if not user_groups.intersection(page.groups_id):
                    page.is_visible = False
        return res


class Menu(models.Model):
    _inherit = "website.menu"

    def _compute_visible(self):
        res = super()._compute_visible()
        for menu in self:
            if menu.is_visible and menu.group_ids:
                user_groups = set(self.env.user.groups_id)
                if not user_groups.intersection(menu.group_ids):
                    menu.is_visible = False
        return res
