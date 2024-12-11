odoo.define('pos_meal_voucher_custom_payment_terminal.devices', function (require) {
    "use strict";

    var devices = require('point_of_sale.devices');

    devices.ProxyDevice.include({
        get_data_send: function(order, line, currency_iso) {
            let data = this._super.apply(this, arguments);
            if (line.is_ok_apply_meal_voucher_amount() && this.pos.config.max_meal_voucher_amount > 0) {
                let amount = data.amount;
                let order_amount_eligible = order.get_total_meal_voucher_eligible();
                amount = Math.max(0, Math.min(amount, order_amount_eligible, this.pos.config.max_meal_voucher_amount));
                data.amount = amount;
            }
            return data;
        },
    });
});
