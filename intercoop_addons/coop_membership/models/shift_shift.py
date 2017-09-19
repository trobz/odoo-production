# -*- coding: utf-8 -*-
##############################################################################
#
#    Purchase - Computed Purchase Order Module for Odoo
#    Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, models, _


class ShiftShift(models.Model):
    _inherit = 'shift.shift'

    @api.multi
    def button_done(self):
        '''
        Modify button done for
            - Create Point for FTOP shift on cloturing
                + Deduct 1 if current point > 1
                + Deduct 2 if current point < 1
        '''
        point_counter_env = self.env['shift.counter.event']
        super(ShiftShift, self).button_done()
        for shift in self:
            if shift.shift_type_id.is_ftop:
                for registration in shift.registration_ids:
                    partner = registration.partner_id
                    # do not deduct points in case member's status is 
                    # On Vacation or Exempted
                    if partner.cooperative_state in ('exempted', 'vacation'):
                        continue
                    current_point = partner.final_ftop_point
                    point = 0
                    if current_point >= 1:
                        point = -1
                    else:
                        point = -2
                    # Create Point Counter
                    point_counter_env.sudo().with_context(
                        {'automatic': True}).create({
                            'name': _('Shift Cloture'),
                            'shift_id': shift.id,
                            'type': 'ftop',
                            'partner_id': partner.id,
                            'point_qty': point
                        })

