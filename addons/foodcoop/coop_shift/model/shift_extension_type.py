# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ShiftExtensionType(models.Model):
    _name = "shift.extension.type"
    _description = "Shift Extension Type"

    name = fields.Char(required=True)

    duration = fields.Integer(required=True, help="Default duration (in days)")
