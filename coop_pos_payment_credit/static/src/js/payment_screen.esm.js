import {PaymentScreen} from "@point_of_sale/app/screens/payment_screen/payment_screen";
import {onMounted} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
    setup() {
        super.setup(...arguments);
        // OCA's setup() adds the auto-apply credit line synchronously.
        // Process it after mount so the RPC call doesn't block rendering.
        onMounted(() => this._processAutoCreditLines());
    },

    async _processAutoCreditLines() {
        const order = this.currentOrder;
        const lines = (order.payment_ids || []).filter(
            (line) =>
                line.payment_method_id?.use_payment_terminal === "credit" &&
                line.payment_method_id?.auto_apply_credit_amount &&
                !line.is_done()
        );
        for (const line of lines) {
            await this.processAutoCreditPaymentLine(line);
        }
    },
});
