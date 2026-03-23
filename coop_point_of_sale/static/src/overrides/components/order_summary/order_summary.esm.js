import {OrderSummary} from "@point_of_sale/app/screens/product_screen/order_summary/order_summary";
import {patch} from "@web/core/utils/patch";

patch(OrderSummary.prototype, {
    _setValue(val) {
        const {numpadMode} = this.pos;
        const selectedLine = this.currentOrder.get_selected_orderline();
        if (selectedLine) {
            if (numpadMode === "quantity") {
                if (val === "0" && this.pos.config.qty_zero_remove_line) {
                    this.currentOrder.removeOrderline(selectedLine);
                    return;
                }
            }
        }
        return super._setValue(...arguments);
    },
});
