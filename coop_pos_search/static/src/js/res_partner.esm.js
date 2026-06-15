import {ResPartner} from "@point_of_sale/app/models/res_partner";
import {patch} from "@web/core/utils/patch";

patch(ResPartner.prototype, {
    exactMatch(searchWord) {
        const fields = ["barcode", "phone", "mobile", "barcode_base"];
        return fields.some(
            (field) =>
                this[field] && this[field].toString().toLowerCase() === searchWord
        );
    },
});
