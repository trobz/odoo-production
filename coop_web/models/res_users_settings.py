# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResUsersSettings(models.Model):
    _inherit = "res.users.settings"

    persistent_classic_theme = fields.Boolean(default=False)
