import {AlertDialog} from "@web/core/confirmation_dialog/confirmation_dialog";
import {OrderSummary} from "@point_of_sale/app/screens/product_screen/order_summary/order_summary";
import {ProductScreen} from "@point_of_sale/app/screens/product_screen/product_screen";
import {_t} from "@web/core/l10n/translation";
import {patch} from "@web/core/utils/patch";

patch(OrderSummary.prototype, {
    /** @override **/
    _handleNegationOnFirstInput(buffer, key, selectedLine) {
        if (
            !this.pos.user.raw.hasGroupNegativeQty &&
            this.pos.numpadMode === "quantity" &&
            key === "-"
        ) {
            this.dialog.add(AlertDialog, {
                title: _t("Not Allowed"),
                body: _t("You do not have permission to set negative quantity."),
            });
            const buffer = selectedLine.get_quantity();
            this.numberBuffer.state.buffer = buffer.toString();
            return buffer;
        }
        return super._handleNegationOnFirstInput(buffer, key, selectedLine);
    },
});

patch(ProductScreen.prototype, {
    get hasManualDiscount() {
        const res = this.pos.config.manual_discount;
        if (res) {
            return this.pos.user.raw.hasGroupDiscount;
        }
        return res;
    },
    get hasMinusControlRights() {
        return this.pos.user.raw.hasGroupNegativeQty;
    },
    get hasPriceControlRights() {
        const res = this.pos.cashierHasPriceControlRights();
        if (res) {
            return this.pos.user.raw.hasGroupPriceControl;
        }
        return res;
    },
    getNumpadButtons() {
        const buttons = super.getNumpadButtons();
        buttons.forEach((button) => {
            if (button.value === "discount") {
                button.disabled = !this.hasManualDiscount;
            } else if (button.value === "price") {
                button.disabled = !this.hasPriceControlRights;
            } else if (button.value === "-") {
                button.disabled = !this.hasMinusControlRights;
            }
        });
        return buttons;
    },
});
