import {TicketScreen} from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import {_t} from "@web/core/l10n/translation";
import {patch} from "@web/core/utils/patch";

patch(TicketScreen.prototype, {
    get emptyOrdersText() {
        return this.pos.data.network.loading ? _t("Loading...") : _t("No orders found");
    },
});
