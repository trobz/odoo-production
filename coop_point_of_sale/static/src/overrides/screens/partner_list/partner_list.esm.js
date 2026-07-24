import {PartnerLine} from "@point_of_sale/app/screens/partner_list/partner_line/partner_line";
import {PartnerList} from "@point_of_sale/app/screens/partner_list/partner_list";
import {onWillStart} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";
import {user} from "@web/core/user";

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
