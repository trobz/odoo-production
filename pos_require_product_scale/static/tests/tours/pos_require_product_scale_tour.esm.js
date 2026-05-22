import * as Chrome from "@point_of_sale/../tests/tours/utils/chrome_util";
import * as Dialog from "@point_of_sale/../tests/tours/utils/dialog_util";
import * as PaymentScreen from "@point_of_sale/../tests/tours/utils/payment_screen_util";
import * as ProductScreen from "@point_of_sale/../tests/tours/utils/product_screen_util";
import {registry} from "@web/core/registry";

const SCALE_POPUP_TITLE =
    "Attention: One or more items to be weighed show a round weight";

// Tour 1: to_weight product, qty=1, setting ON → popup shown → cancel → stays on product screen
registry.category("web_tour.tours").add("pos_require_scale_cancel_tour", {
    steps: () =>
        [
            Chrome.startPoS(),
            Dialog.confirm("Open Register"),
            ProductScreen.clickDisplayedProduct("Weighted Product"),
            ProductScreen.clickPayButton(false),
            Dialog.is({title: SCALE_POPUP_TITLE}),
            Dialog.cancel(),
            ProductScreen.isShown(),
            Chrome.endTour(),
        ].flat(),
});

// Tour 2: to_weight product, qty=1, setting ON → popup shown → confirm → payment screen
registry.category("web_tour.tours").add("pos_require_scale_confirm_tour", {
    steps: () =>
        [
            Chrome.startPoS(),
            Dialog.confirm("Open Register"),
            ProductScreen.clickDisplayedProduct("Weighted Product"),
            ProductScreen.clickPayButton(false),
            Dialog.is({title: SCALE_POPUP_TITLE}),
            Dialog.confirm(),
            PaymentScreen.isShown(),
            Chrome.endTour(),
        ].flat(),
});

// Tour 3: normal product (to_weight=False), qty=1, setting ON → no popup → payment screen
registry.category("web_tour.tours").add("pos_require_scale_normal_product_tour", {
    steps: () =>
        [
            Chrome.startPoS(),
            Dialog.confirm("Open Register"),
            ProductScreen.clickDisplayedProduct("Normal Product"),
            ProductScreen.clickPayButton(false),
            Dialog.isNot(),
            PaymentScreen.isShown(),
            Chrome.endTour(),
        ].flat(),
});

// Tour 4: to_weight product, qty=1, setting OFF → no popup → payment screen
registry.category("web_tour.tours").add("pos_require_scale_setting_disabled_tour", {
    steps: () =>
        [
            Chrome.startPoS(),
            Dialog.confirm("Open Register"),
            ProductScreen.clickDisplayedProduct("Weighted Product"),
            ProductScreen.clickPayButton(false),
            Dialog.isNot(),
            PaymentScreen.isShown(),
            Chrome.endTour(),
        ].flat(),
});
