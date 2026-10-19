/* global Sha1 */
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
        const managers = this.get_cashier().raw._manager_auth_users || [];

        if (!managers.length) {
            await new Promise((resolve) => {
                this.dialog.add(
                    AlertDialog,
                    {
                        title: _t("Manager Authentication Unavailable"),
                        body: _t(
                            "No manager with a POS Security PIN is available for authorization."
                        ),
                    },
                    {onClose: resolve}
                );
            });
            return false;
        }

        while (true) {
            const auth = await makeAwaitable(this.dialog, ManagerAuthPopup, {
                title: _t("Manager Login Required"),
                getPayload: (value) => value,
            });

            if (!auth?.login || !auth?.pin) {
                return false;
            }

            const manager = managers.find((user) => user.login === auth.login);
            if (!manager) {
                await new Promise((resolve) => {
                    this.dialog.add(
                        AlertDialog,
                        {
                            title: _t("Unknown Manager Login"),
                            body: _t("No manager was found with that login."),
                        },
                        {onClose: resolve}
                    );
                });
                continue;
            }

            if (Sha1.hash(auth.pin) === manager._pin) {
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
