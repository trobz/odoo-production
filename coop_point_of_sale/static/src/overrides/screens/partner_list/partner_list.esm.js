import {PartnerLine} from "@point_of_sale/app/screens/partner_list/partner_line/partner_line";
import {patch} from "@web/core/utils/patch";

patch(PartnerLine.prototype, {
    getPartnerImageUrl(id) {
        return "/web/image?model=res.partner&id=" + id + "&field=image_128";
    },
});
