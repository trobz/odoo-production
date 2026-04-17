from odoo import _, models


class ShiftShift(models.Model):
    _inherit = "shift.shift"

    def button_done(self):
        """
        @Overide the function to create -1 point counter for standard registration
        which is canceled
        """
        res = super().button_done()
        SCEvent = (
            self.env["shift.counter.event"]
            .sudo()
            .with_context(
                automatic=True,
            )
        )
        for shift in self:
            for record in shift.registration_ids:
                if record.state == "cancel" and record.shift_type == "standard":
                    vals = {
                        "name": _("Annuler votre participation"),
                        "type": "standard",
                        "partner_id": record.partner_id.id,
                        "point_qty": -1,
                        "shift_id": record.shift_id.id,
                    }
                    if record.partner_id.final_ftop_point > 0:
                        vals["type"] = "ftop"
                    SCEvent.create(vals)
        return res
