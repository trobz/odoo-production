odoo.define('pos_barcode_discount.db', function (require) {
    "use strict";

    const screens = require('point_of_sale.screens');
    const core = require('web.core');
    const _t = core._t;

    screens.ScreenWidget.include({
        barcode_discount_action: function(code){
            const self = this;
            const super_func = self._super;
            const super_arguments = arguments;
            if (this.pos.config.discount_by_category && this.pos.config.discount_category_all_ids.length > 0) {
                const last_orderline = this.pos.get_order().get_last_orderline();
                const product = last_orderline.product;
                if (product.categ_id.length == 2) {
                    if (this.pos.config.discount_category_all_ids.indexOf(product.categ_id[0]) !== -1)  {
                        // Confirm
                        this.gui.show_popup('confirm', {
                            'title': _t('Confirming'),
                            'body': _t('Attention, you are applying') + 
                                ' ' + code.value + '% ' +
                                _t('discount for the product') +
                                ' ' + product.display_name + '. ' +
                                _t('Are you sure that you would like to proceed it?'),
                            confirm: function () {
                                super_func.apply(self, super_arguments);
                            },
                        });
                    }
                    else {
                        // Warning
                        this.gui.show_popup('error', {
                            'title': _t('Error'),
                            'body':  _t('This discount does not apply for the product') +
                                ' ' + product.display_name + '.'
                        });
                    }
                    return
                }
            }
            return self._super(code);
        },
    });
});
