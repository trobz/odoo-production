
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

odoo.define("pos_meal_voucher_custom_payment_terminal.models", function (require) {
    "use strict";

    var models = require("point_of_sale.models");
    var _super_paymentline = models.Paymentline.prototype;
    var Paymentline = models.Paymentline.extend({
        auto_apply_meal_voucher_amount: function() {
            let flag = _super_paymentline.auto_apply_meal_voucher_amount.apply(this, arguments);
            if (flag && this.pos.config.iface_payment_terminal_return){
                // No apply meal amount if enable payment terminal
                flag = !this.get_automatic_payment_terminal();
            }
            return flag;
        },
        get_automatic_payment_terminal: function() {
            let flag = _super_paymentline.get_automatic_payment_terminal.apply(this, arguments);
            if (flag && this.is_ok_apply_meal_voucher_amount() && this.pos.config.max_meal_voucher_amount > 0){
                // No auto send to payment terminal if applying 0 meal voucher amount
                var order = this.pos.get_order();
                var order_amount_eligible = order.get_total_meal_voucher_eligible();
                var amount = order.get_due(this);
                amount = Math.max(0, Math.min(amount, order_amount_eligible, this.pos.config.max_meal_voucher_amount));
                if (amount <= 0) {
                    flag = false;
                }
            }
            return flag;
        },
    });

    models.Paymentline = Paymentline;

});
