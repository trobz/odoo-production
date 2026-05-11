from odoo import api, fields, models
from odoo.http import request


class Page(models.Model):
    _inherit = "website.page"

    group_ids = fields.Many2many(
        string="Groups",
        comodel_name="res.groups",
        relation="res_group_website_page_rel",
        column_1="page_id",
        column_2="group_id",
    )

    @api.multi
    def _compute_visible(self):
        for rec in self:
            visible = rec.website_published and (
                not rec.date_publish or rec.date_publish < fields.Datetime.now()
            )
            if visible and request and rec.group_ids:
                user_groups = set(request.env.user.groups_id)
                if len(user_groups.intersection(rec.group_ids)) == 0:
                    visible = False
            rec.is_visible = visible


class Menu(models.Model):
    _inherit = "website.menu"

    group_ids = fields.Many2many(
        string="Groups",
        comodel_name="res.groups",
        relation="res_group_website_menu_rel",
        column_1="menu_id",
        column_2="group_id",
    )

    @api.multi
    def _compute_visible(self):
        for rec in self:
            visible = True
            if (
                rec.page_id
                and not rec.page_id.sudo().is_visible
                and not rec.user_has_groups("base.group_user")
            ):
                visible = False
            if visible and rec.group_ids:
                user_groups = set(self.env.user.groups_id)
                if len(user_groups.intersection(rec.group_ids)) == 0:
                    visible = False
            rec.is_visible = visible
