# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2012 Domsense s.r.l. (<http://www.domsense.com>).
#    Copyright (C) 2014 Agile Business Group sagl (<http://www.agilebg.com>)
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

from openerp.osv import orm, fields


class AccountTaxCode(orm.Model):
    _inherit = "account.tax.code"
    _columns = {
        'vat_on_payment_related_tax_code_id': fields.many2one(
            'account.tax.code', 'Shadow Tax code for VAT on payment',
            help="Related tax code used for real registrations on a "
                 "VAT on payment basis. Set the shadow tax code here"),
    }
