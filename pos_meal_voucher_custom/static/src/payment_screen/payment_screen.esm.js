// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import {AlertDialog} from "@web/core/confirmation_dialog/confirmation_dialog";
import {PaymentScreen} from "@point_of_sale/app/screens/payment_screen/payment_screen";
import {_t} from "@web/core/l10n/translation";
import {patch} from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
    is_ok_apply_meal_voucher_amount(paymentMethod, manualMealVoucher) {
        return (
            manualMealVoucher === true ||
            (paymentMethod.meal_voucher_type !== false &&
                this.pos.config.max_meal_voucher_amount > 0)
        );
    },
    auto_apply_meal_voucher_amount(paymentMethod, manualMealVoucher) {
        return this.is_ok_apply_meal_voucher_amount(paymentMethod, manualMealVoucher);
    },
    async addNewPaymentLine(paymentMethod, manualMealVoucher = false) {
        const result = await super.addNewPaymentLine(paymentMethod);
        if (this.auto_apply_meal_voucher_amount(paymentMethod, manualMealVoucher)) {
            const mealVoucherPayments = this.currentOrder.payment_ids.filter(
                (paymentLine) => paymentLine.is_meal_voucher()
            );
            if (mealVoucherPayments.length === 1) {
                this.apply_meal_amount(mealVoucherPayments[0]);
            } else {
                this.dialog.add(AlertDialog, {
                    title: _t("Error Meal Voucher"),
                    body: _t("There is already an Meal Voucher payment in progress."),
                });
            }
        }
        return result;
    },
    apply_meal_amount(paymentLine) {
        paymentLine.set_amount(
            Math.max(
                0,
                Math.min(this.mealVoucherEligibleAmount, this.maxMealVoucherAmount)
            )
        );
        return;
    },
});
