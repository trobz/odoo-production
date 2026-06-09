import {PartnerList} from "@point_of_sale/app/screens/partner_list/partner_list";
import {patch} from "@web/core/utils/patch";
import {unaccent} from "@web/core/utils/strings";

patch(PartnerList.prototype, {
    getPartners() {
        const searchWord = unaccent(
            (this.state.query || "").trim(),
            false
        ).toLowerCase();
        const availablePartners = super.getPartners();
        if (availablePartners.length > 0) {
            return availablePartners.filter((partner) =>
                partner.exactMatch(searchWord)
            );
        }
        return availablePartners;
    },
});
