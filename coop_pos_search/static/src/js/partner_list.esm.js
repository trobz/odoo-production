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
        const numberString = searchWord.replace(/[+\s()-]/g, "");
        const isSearchWordNumber = /^[0-9]+$/.test(numberString);
        if (isSearchWordNumber) {
            return availablePartners.filter((partner) =>
                partner.exactMatch(numberString)
            );
        }
        return availablePartners;
    },
});
