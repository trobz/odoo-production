from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Use exempted_member_status of leave to recompute member state
    @api.depends(
        "is_blocked",
        "final_standard_point",
        "final_ftop_point",
        "shift_type",
        "date_alert_stop",
        "date_delay_stop",
        "leave_ids.state",
        "leave_ids.forced_member_status",
    )
    def _compute_working_state(self):
        """Override method from coop_shift for parental leave improvement"""
        today = fields.Date.today()
        res = super()._compute_working_state()
        for partner in self:
            # Check member force status in shift.leave
            parental_leaves = partner.leave_ids.filtered(
                lambda leave: leave.is_parental_leave
                and leave.start_date <= today <= leave.stop_date
                and leave.forced_member_status
            )
            # If member has one parental_leave and does not provide birthday
            #  certificate set member status to exempted
            if parental_leaves and parental_leaves[0]:
                state = parental_leaves[0].forced_member_status
                if partner.working_state != state:
                    partner.working_state = state
            # If there isn't any parental leave, fallback to super()
        return res
