/* global Sha1 */
/* License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
import {AlertDialog} from "@web/core/confirmation_dialog/confirmation_dialog";
import {NumberPopup} from "@point_of_sale/app/utils/input_popups/number_popup";
import {PosStore} from "@point_of_sale/app/store/pos_store";
import {_t} from "@web/core/l10n/translation";
import {makeAwaitable} from "@point_of_sale/app/store/make_awaitable_dialog";
import {patch} from "@web/core/utils/patch";

patch(PosStore.prototype, {
    async processCreditPayment(payment) {
        // Managers (and admins) are trusted; only cashiers must confirm with a PIN.
        if (this.get_cashier()._role !== "manager") {
            const confirmed = await this._askCreditPin();
            if (!confirmed) {
                return {
                    status: "error",
                    error: _t("Authentication failed!"),
                };
            }
        }
        return super.processCreditPayment(payment);
    },

    async _askCreditPin() {
        const currentPin = this.get_cashier().raw._pin;

        if (!currentPin) {
            return false;
        }

        while (true) {
            const enteredPin = await makeAwaitable(this.dialog, NumberPopup, {
                title: _t("Security PIN Required"),
                subtitle: _t("Enter your PIN to confirm this credit payment."),
                formatDisplayedValue: (x) => x.replace(/./g, "•"),
                isValid: (val) => val.length > 0,
            });

            if (!enteredPin) {
                return false;
            }

            if (Sha1.hash(enteredPin) === currentPin) {
                return true;
            }

            await new Promise((resolve) => {
                this.dialog.add(
                    AlertDialog,
                    {
                        title: _t("Incorrect PIN"),
                        body: _t("The PIN you entered is incorrect. Please try again."),
                    },
                    {onClose: resolve}
                );
            });
        }
    },
});
