// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

odoo.define("pos_meal_voucher_custom.screens", function (require) {
    "use strict";

    var screens = require("point_of_sale.screens");

    screens.PaymentScreenWidget.include({
        click_paymentmethods: function(id) {
            this._super.apply(this, arguments);
            // Update the amount based on the meal voucher amount
            this.apply_meal_amount();
        },
        apply_meal_amount: function() {
            var self = this;
            var order = this.pos.get_order();
            var order_amount_eligible = order.get_total_meal_voucher_eligible();
            var line = order.selected_paymentline;
            if (line.auto_apply_meal_voucher_amount() && this.pos.config.max_meal_voucher_amount > 0) {
                var amount = order.get_due(line);
                amount = Math.max(0, Math.min(amount, order_amount_eligible, this.pos.config.max_meal_voucher_amount));
                var amountFormatted = self.format_currency_no_symbol(amount);
                line.set_amount(amount);
                self.order_changes();
                self.render_paymentlines();
                self.$('.paymentline.selected .edit').text(amountFormatted);
            }
        },
    });
});
