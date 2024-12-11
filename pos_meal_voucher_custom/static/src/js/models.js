
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

odoo.define("pos_meal_voucher_custom.models", function (require) {
    "use strict";

    var models = require("point_of_sale.models");

    var Paymentline = models.Paymentline.extend({
        is_ok_apply_meal_voucher_amount: function() {
            return (
                this.manual_meal_voucher === true ||
                (
                    this.cashregister.journal.meal_voucher_type &&
                    this.cashregister.journal.meal_voucher_type !== undefined
                )
            );
        },
        auto_apply_meal_voucher_amount: function(){
            // a hook to be called by child module
            return this.is_ok_apply_meal_voucher_amount();
        }
    });

    models.Paymentline = Paymentline;

});
