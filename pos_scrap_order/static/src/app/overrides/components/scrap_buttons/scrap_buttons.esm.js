import {ProductScreen} from "@point_of_sale/app/screens/product_screen/product_screen";
import {patch} from "@web/core/utils/patch";

patch(ProductScreen.prototype, {
    get showScrapButtons() {
        const opt = this.pos.config.scrap_order_option;
        return opt !== undefined && opt !== "no";
    },
    clickScrap() {
        this.pos.showScreen("ScrapScreen");
    },
    clickScrapList() {
        this.pos.showScreen("ScrapListScreen");
    },
});
