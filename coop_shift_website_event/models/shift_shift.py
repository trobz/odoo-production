from odoo import models


class ShiftShift(models.Model):
    _inherit = "shift.shift"

    def _get_menus_update_by_field(self, menus_state_by_field, force_update=None):
        force_update = force_update or []
        menus_update_by_field = {}
        for field_name in self._get_menu_update_fields():
            if field_name in force_update:
                menus_update_by_field[field_name] = self
                continue
            menus_update_by_field[field_name] = menus_state_by_field[field_name][
                "activated"
            ].filtered(lambda event, fname=field_name: not event[fname])
            menus_update_by_field[field_name] |= menus_state_by_field[field_name][
                "deactivated"
            ].filtered(lambda event, fname=field_name: event[fname])
        return menus_update_by_field
