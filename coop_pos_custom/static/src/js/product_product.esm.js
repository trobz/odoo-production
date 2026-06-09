import {ProductProduct} from "@point_of_sale/app/models/product_product";
import {patch} from "@web/core/utils/patch";

patch(ProductProduct.prototype, {
    exactMatch(searchWord = false) {
        if (searchWord) {
            const fields = ["display_name", "barcode", "default_code"];
            return fields.some(
                (field) => this[field] && this[field].toLowerCase() === searchWord
            );
        }
        return super.exactMatch();
    },
});
