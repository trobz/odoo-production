import {TicketScreen} from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import {patch} from "@web/core/utils/patch";

patch(TicketScreen.prototype, {
    shouldHideDeleteButton(order) {
        if (!this.pos.user.raw.hasGroupDeleteOrder) {
            return true;
        }
        return super.shouldHideDeleteButton(order);
    },
});
