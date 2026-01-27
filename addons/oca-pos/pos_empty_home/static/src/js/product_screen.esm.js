import {ProductScreen} from "@point_of_sale/app/screens/product_screen/product_screen";
import {patch} from "@web/core/utils/patch";

patch(ProductScreen.prototype, {
    get isShowEmptyHome() {
        return (
            this.pos.config.iface_empty_home &&
            this.pos.session._has_available_products &&
            !this.pos.selectedCategory &&
            this.searchWord == ""
        );
    },

    get productsToDisplay() {
        return this.isShowEmptyHome ? [] : super.productsToDisplay;
    },
});
