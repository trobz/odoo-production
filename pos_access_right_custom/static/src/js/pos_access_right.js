
odoo.define('pos_access_right_custom.pos_access_right', function (require) {
    "use strict";

    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var _t = core._t;

    screens.NumpadWidget.include({
        checkDeletePaymentOrder: function(){
            var line = this.pos.get_order().selected_paymentline;
            if (line && this.pos.get_cashier().groups_id.indexOf(
                this.pos.config.group_delete_order_id[0]) === -1) {
                this.gui.show_popup('error', {
                    'title': _t('Change Order Value - Unauthorized function'),
                    'body':  _t('Please, ask your manager to do it.'),
                });
                return false;
            }
            return true;
        },
    });

});
