import {AlertDialog} from "@web/core/confirmation_dialog/confirmation_dialog";
import {OrderTabs} from "@point_of_sale/app/components/order_tabs/order_tabs";
import {_t} from "@web/core/l10n/translation";
import {patch} from "@web/core/utils/patch";

patch(OrderTabs.prototype, {
    newFloatingOrder() {
        if (!this.pos.user.raw.hasGroupMultiOrder) {
            this.dialog.add(AlertDialog, {
                title: _t("Not Allowed"),
                body: _t("You do not have permission to open multiple order."),
            });
            return;
        }
        return super.newFloatingOrder();
    },
});
