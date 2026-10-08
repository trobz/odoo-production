import {PosOrder} from "@point_of_sale/app/models/pos_order";
import {patch} from "@web/core/utils/patch";

patch(PosOrder.prototype, {
    setup(vals) {
        super.setup(vals);
        // When invoicing is disabled, active orders must never be invoiced.
        if (!this.config.customer_invoicing && !this.finalized) {
            this.to_invoice = false;
        }
    },

    set_partner(partner) {
        super.set_partner(partner);
        // Core auto-enables invoicing for company partners; undo it when disabled.
        if (!this.config.customer_invoicing) {
            this.to_invoice = false;
        }
    },
});
