import {ProductScreen} from "@point_of_sale/app/screens/product_screen/product_screen";
import {patch} from "@web/core/utils/patch";
import {unaccent} from "@web/core/utils/strings";

patch(ProductScreen.prototype, {
    getProductsBySearchWord(searchWord) {
        const words = unaccent(searchWord.toLowerCase(), false);
        const filteredProducts = super.getProductsBySearchWord(searchWord);
        if (filteredProducts) {
            const exactProduct = filteredProducts.find((product) =>
                product.exactMatch(words)
            );
            return exactProduct ? [exactProduct] : [];
        }
        return filteredProducts;
    },
});
