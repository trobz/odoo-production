from odoo import fields, models


class ShiftStage(models.Model):
    _name = "shift.stage"
    _description = "Shift Stage"
    _order = "sequence, name"

    name = fields.Char(string="Stage Name", required=True, translate=True)
    sequence = fields.Integer(default=1)
    # legend_* required: inherited event.event kanban fields read stage_id.legend_*.
    legend_blocked = fields.Char(
        "Red Kanban Label",
        default=lambda s: s.env._("Blocked"),
        translate=True,
        prefetch="legend",
        required=True,
    )
    legend_done = fields.Char(
        "Green Kanban Label",
        default=lambda s: s.env._("Ready for Next Stage"),
        translate=True,
        prefetch="legend",
        required=True,
    )
    legend_normal = fields.Char(
        "Grey Kanban Label",
        default=lambda s: s.env._("In Progress"),
        translate=True,
        prefetch="legend",
        required=True,
    )
