/* License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
import {PaymentScreen} from "@point_of_sale/app/screens/payment_screen/payment_screen";
import {PinCancelledError} from "@pos_payment_credit_pin/js/pos_store.esm";
import {patch} from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
    async processCreditPaymentLine(paymentLine) {
        try {
            return await super.processCreditPaymentLine(paymentLine);
        } catch (e) {
            if (e instanceof PinCancelledError) {
                // User cancelled PIN — leave payment line for retry, show nothing
                return;
            }
            throw e;
        }
    },
});
