import {PaymentScreen} from "@point_of_sale/app/screens/payment_screen/payment_screen";
import {patch} from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
    auto_apply_meal_voucher_amount(paymentMethod, manualMealVoucher) {
        const flag = super.auto_apply_meal_voucher_amount(
            paymentMethod,
            manualMealVoucher
        );
        if (
            flag &&
            paymentMethod.payment_method_type === "terminal" &&
            paymentMethod.oca_payment_terminal_return
        ) {
            // No apply meal amount if enable payment terminal
            return false;
        }
        return flag;
    },
});
