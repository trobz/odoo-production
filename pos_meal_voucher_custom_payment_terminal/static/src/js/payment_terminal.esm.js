import {OCAPaymentTerminal} from "@pos_payment_terminal/app/payment_terminal.esm";
import {patch} from "@web/core/utils/patch";

patch(OCAPaymentTerminal.prototype, {
    _get_amount_to_pay() {
        const order = this.pos.get_order();
        const paymentLine = order.get_selected_paymentline();
        const amount = paymentLine.amount;
        if (
            paymentLine.is_meal_voucher() &&
            this.pos.config.max_meal_voucher_amount > 0
        ) {
            const amount_max = this.pos.config.max_meal_voucher_amount;
            const amount_eligible = order.get_total_meal_voucher_eligible();
            const amount_due = order.get_due();
            return Math.max(
                0,
                Math.min(amount, amount_eligible, amount_due, amount_max)
            );
        }
        return amount;
    },
    get fast_payments() {
        const res = super.fast_payments;
        const amount_to_pay = this._get_amount_to_pay();
        if (amount_to_pay <= 0) {
            return false;
        }
        return res;
    },
    _ocaPaymentTerminalGetData(uuid) {
        const data = super._ocaPaymentTerminalGetData(uuid);
        data.amount = this._get_amount_to_pay();
        return data;
    },
});
