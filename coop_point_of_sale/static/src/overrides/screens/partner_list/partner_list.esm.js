import {PartnerList} from "@point_of_sale/app/screens/partner_list/partner_list";
import {PartnerLine} from "@point_of_sale/app/screens/partner_list/partner_line/partner_line";
import {patch} from "@web/core/utils/patch";
import {user} from "@web/core/user";
import {onWillStart} from "@odoo/owl";

patch(PartnerLine.prototype, {
    getPartnerImageUrl(id) {
        return "/web/image?model=res.partner&id=" + id + "&field=image_128";
    },
});

patch(PartnerList.prototype, {
    setup() {
        super.setup();
        this.state.allowPartnerCreation = false;
        onWillStart(async () => {
            this.state.allowPartnerCreation = await user.checkAccessRight(
                "res.partner",
                "create"
            );
        });
    },
});
