import {ProductScreen} from "@point_of_sale/app/screens/product_screen/product_screen";
import {patch} from "@web/core/utils/patch";
import {unaccent} from "@web/core/utils/strings";

patch(ProductScreen.prototype, {
    getProductsBySearchWord(searchWord) {
        const words = unaccent(searchWord.toLowerCase(), false);
        const filteredProducts = super.getProductsBySearchWord(searchWord);
        const numberString = words.replace(/[+\s()-]/g, "");
        const isSearchWordNumber =
            numberString.length >= 5 && /^[0-9]+$/.test(numberString);

        if (isSearchWordNumber) {
            return filteredProducts.filter((product) => product.exactMatch(words));
        }
        return filteredProducts;
    },
});
