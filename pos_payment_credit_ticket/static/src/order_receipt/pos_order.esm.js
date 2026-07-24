import {PosOrder} from "@point_of_sale/app/models/pos_order";
import {patch} from "@web/core/utils/patch";

patch(PosOrder.prototype, {
    // @override
    export_for_printing(baseUrl, headerData) {
        const result = super.export_for_printing(baseUrl, headerData);
        if (this.get_partner()) {
            result.customer_info = {
                available_credit: this.getAvailableCredit(),
                name: this.partner_id?.name || "",
            };
        } else {
            result.customer_info = null;
        }
        return result;
    },
    getAvailableCredit() {
        const partner = this.partner_id;
        return partner?.credit_amount || 0;
    },
});
