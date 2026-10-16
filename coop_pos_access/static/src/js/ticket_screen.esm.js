import {TicketScreen} from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import {patch} from "@web/core/utils/patch";

patch(TicketScreen.prototype, {
    setup() {
        super.setup();
        this.allowRefund = this.pos.user.raw.hasGroupRefund || false;
    },
});
