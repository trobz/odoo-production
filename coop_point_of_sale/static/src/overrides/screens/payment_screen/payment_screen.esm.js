import {AlertDialog} from "@web/core/confirmation_dialog/confirmation_dialog";
import {PaymentScreen} from "@point_of_sale/app/screens/payment_screen/payment_screen";
import {VerifyPaymentDialog} from "@coop_point_of_sale/overrides/components/dialogs/verify_payment.esm";
import {_t} from "@web/core/l10n/translation";
import {patch} from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
    _getAccountJournal(paymentLine) {
        return paymentLine.payment_method_id?.raw?.journal_id || null;
    },

    _getJournalsToCheck() {
        return this.pos.config.raw.account_journal_ids || [];
    },

    _prepareVerifyPaymentParams(paymentMethod) {
        const payableTo = this.pos.config.payable_to || "";
        const thanks_message = _t("Please check the cheque: ");
        const amount = _t("The amount");
        const date = _t("The date");
        const order_messages = _t("The order: " + payableTo);
        const signature = _t("The presence of a signature");
        return {
            thanks_message: thanks_message,
            amount: amount,
            date: date,
            order_messages: order_messages,
            signature: signature,
            cancel_callback: () => {
                return;
            },
            confirm: () => {
                return super.addNewPaymentLine(paymentMethod);
            },
        };
    },

    async addNewPaymentLine(paymentMethod) {
        if (!this.pos.config.enable_popup_verify_payment) {
            return super.addNewPaymentLine(paymentMethod);
        }

        const currentJournalId = paymentMethod.raw.journal_id;
        const configJournalIds = this._getJournalsToCheck();

        if (!currentJournalId || !configJournalIds.includes(currentJournalId)) {
            return super.addNewPaymentLine(paymentMethod);
        }
        const sameMethodPaymentLines = this.paymentLines.filter((payment) => {
            const journalId = this._getAccountJournal(payment);
            return journalId === currentJournalId;
        });
        if (sameMethodPaymentLines.length) {
            this.dialog.add(AlertDialog, {
                title: _t("Error"),
                body: _t(
                    "A payment line with the same Account Journal already exists."
                ),
            });
            return;
        }
        const params = this._prepareVerifyPaymentParams(paymentMethod);
        this.dialog.add(VerifyPaymentDialog, params);
    },
});
