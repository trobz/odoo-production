import {PosStore} from "@point_of_sale/app/store/pos_store";
import {patch} from "@web/core/utils/patch";

patch(PosStore.prototype, {
    async logEmployeeMessage(action, message) {
        // Pos_hr (multi-employee) has its own implementation.
        if (this.config.module_pos_hr) {
            return super.logEmployeeMessage(...arguments);
        }
        // Core uses `this.user.partner_id.id`, but the partner of the logged in
        // user is not loaded in the POS when it is not a customer (see the
        // domain in models/res_partner.py), so `partner_id` is undefined.
        // The raw record always holds the id.
        await this.data.call(
            "pos.session",
            "log_partner_message",
            [this.session.id, this.user.raw.partner_id, action, message],
            {},
            true
        );
    },
});
