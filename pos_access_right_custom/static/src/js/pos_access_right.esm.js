import {PosOrderline} from "@point_of_sale/app/models/pos_order_line";
import {_t} from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

patch(PosOrderline.prototype, {
    setup(vals) {
        super.setup(vals);
    },
    set_quantity(quantity, keep_price) {
        if (
            !this.order_id.user.raw.hasGroupDeleteOrder &&
            this.order_id.payment_ids.length > 0
        ) {
            return {
                title: _t("Change Order Value - Unauthorized function"),
                body: _t("Please, ask your manager to do it"),
            };
        } else {
            return super.set_quantity(quantity, keep_price);
        }
    }
})
