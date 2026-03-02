# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ShiftTypeMail(models.Model):
    _inherit = "event.type.mail"
    _name = "shift.type.mail"
    _description = "Mail Scheduling on Shift Category"

    event_type_id = fields.Many2one("shift.type", ondelete="cascade", required=True)
