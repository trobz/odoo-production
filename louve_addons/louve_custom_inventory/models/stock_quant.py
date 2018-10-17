# -*- coding: utf-8 -*-

from openerp import api, fields, models
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    product_type = fields.Char(
        compute='_compute_product_type',
        store=True
    )

    def _compute_product_type(self):
        for quant in self:
            quant.product_type = quant.product_id.type
        return True

    # Custom Section
    @api.multi
    def update_product_type(self):
        session_ids = self.ids
        num_session_per_job = 500
        splited_session_list = \
            [session_ids[i: i + num_session_per_job]
             for i in range(0, len(session_ids), num_session_per_job)]
        # Prepare session for job
        session = ConnectorSession(self._cr, self._uid)
        # Create jobs
        for session_list in splited_session_list:
            update_product_type_stock_quant_session_job.delay(
                session, 'stock.quant', session_list)
        return True


@job
def update_product_type_stock_quant_session_job(
        session, model_name, session_list):
    """ Job for compute cycle """
    quants = session.env[model_name].browse(session_list)
    quants._compute_product_type()
