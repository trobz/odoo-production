from odoo import fields, models


class WebsiteMenu(models.Model):
    _inherit = "website.menu"

    force_invisible = fields.Boolean(
        default=False,
        help="If checked, this menu item will always be hidden from the website",
    )

    def _compute_visible(self):
        """Override visibility computation to respect force_invisible flag."""
        res = super()._compute_visible()
        for menu in self:
            if menu.force_invisible:
                menu.is_visible = False
        return res
