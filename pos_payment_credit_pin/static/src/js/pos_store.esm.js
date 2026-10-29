/* License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
import {AlertDialog} from "@web/core/confirmation_dialog/confirmation_dialog";
import {ManagerAuthPopup} from "./manager_auth_popup.esm";
import {PosStore} from "@point_of_sale/app/store/pos_store";
import {_t} from "@web/core/l10n/translation";
import {makeAwaitable} from "@point_of_sale/app/store/make_awaitable_dialog";
import {patch} from "@web/core/utils/patch";

patch(PosStore.prototype, {
    async processCreditPayment(payment) {
        // Managers (and admins) are trusted; cashiers need manager authentication.
        if (this.get_cashier()._role !== "manager") {
            const confirmed = await this._borrowManagerRole();
            if (!confirmed) {
                return {
                    status: "error",
                    error: _t("Authentication failed!"),
                };
            }
        }
        return super.processCreditPayment(payment);
    },

    async _borrowManagerRole() {
        while (true) {
            const auth = await makeAwaitable(this.dialog, ManagerAuthPopup, {
                title: _t("Manager Login Required"),
                getPayload: (value) => value,
            });

            if (!auth?.login || !auth?.pin) {
                return false;
            }

            let verified = false;
            try {
                verified = await this.data.call("res.users", "verify_pos_manager_pin", [
                    auth.login,
                    auth.pin,
                ]);
            } catch {
                // The server round-trip failed (e.g. offline): verification
                // cannot be performed, so authorization must be refused.
                await new Promise((resolve) => {
                    this.dialog.add(
                        AlertDialog,
                        {
                            title: _t("Verification Unavailable"),
                            body: _t(
                                "Could not reach the server to verify the manager PIN. " +
                                    "A network connection is required to authorize a credit payment. " +
                                    "Check the connection and try again."
                            ),
                        },
                        {onClose: resolve}
                    );
                });
                return false;
            }

            if (verified) {
                return true;
            }

            await new Promise((resolve) => {
                this.dialog.add(
                    AlertDialog,
                    {
                        title: _t("Authentication Failed"),
                        body: _t(
                            "No active Point of Sale manager matches this login, or the PIN is incorrect. " +
                                "Check the manager login and PIN, then try again."
                        ),
                    },
                    {onClose: resolve}
                );
            });
        }
    },
});
