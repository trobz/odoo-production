from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.depends(lambda self: (self._rec_name,) if self._rec_name else ())
    def _compute_display_name(self):
        ctx = self._context
        if isinstance(ctx.get('params'), dict) and \
                ctx['params'].get('model') in ['stock.inventory',
                    'purchase.order', 'account.invoice']:
            names = dict(self.with_context(
                display_default_code=False).name_get())
        else:
            names = dict(self.name_get())
        for record in self:
            record.display_name = names.get(record.id, False)
