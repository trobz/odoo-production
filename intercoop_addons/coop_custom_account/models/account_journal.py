# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    deprecated = fields.Boolean("Deprecated", index=True, default=False)

    def _search(self, cr, user, args, offset=0, limit=None, order=None,
                context=None, count=False, access_rights_uid=None):
        for arg in args:
            if 'deprecated' in arg[0]:
                return super(account_journal, self)._search(cr, user, args,
                                                            offset, limit,
                                                            order, context,
                                                            count,
                                                            access_rights_uid)
        args.append(['deprecated', '=', False])
        return super(AccountJournal, self)._search(cr, user, args, offset,
                                                   limit, order, context,
                                                   count, access_rights_uid)
