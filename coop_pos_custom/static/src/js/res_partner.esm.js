import {ResPartner} from "@point_of_sale/app/models/res_partner";
import {patch} from "@web/core/utils/patch";

patch(ResPartner.prototype, {
    exactMatch(searchWord) {
        const fields = [
            "name",
            "barcode",
            "phone",
            "mobile",
            "email",
            "vat",
            "contact_address",
        ];
        return fields.some(
            (field) => this[field] && this[field].toLowerCase() === searchWord
        );
    },
});
