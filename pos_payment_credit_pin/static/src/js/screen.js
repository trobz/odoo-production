/* License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */
   odoo.define('pos_payment_credit_pin.screens', function (require) {
    "use strict";

    var screens = require('point_of_sale.screens');
    var PaymentScreenWidget = screens.PaymentScreenWidget;

    PaymentScreenWidget.include({
        order_is_valid: function(force_validation) {
            var isValid = this._super();
            var self = this;
            var order = this.pos.get_order();
            const paymentlines = order.get_paymentlines();
            if (!force_validation && isValid && paymentlines.length !== 0) {
                for (var i = 0; i < paymentlines.length; i++) {
                    var line = paymentlines[i];
                    if (line && line.get_credit_payment()) {
                        this.gui.sudo().then(function(){
                            self.validate_order('confirm');
                        });
                        return false;
                    }
                }
            }
            return isValid;
        },
    });
});
