import {PosOrder} from "@point_of_sale/app/models/pos_order";
import {patch} from "@web/core/utils/patch";

patch(PosOrder.prototype, {
    set_partner(partner) {
        super.set_partner(partner);
        // Core auto-enables invoicing for company partners; undo it when disabled.
        if (!this.config.customer_invoicing) {
            this.set_to_invoice(false);
        }
    },
});
