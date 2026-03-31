import * as Chrome from "@point_of_sale/../tests/tours/utils/chrome_util";
import * as Dialog from "@point_of_sale/../tests/tours/utils/dialog_util";
import * as Numpad from "@point_of_sale/../tests/tours/utils/numpad_util";
import * as PaymentScreen from "@point_of_sale/../tests/tours/utils/payment_screen_util";
import * as ProductScreen from "@point_of_sale/../tests/tours/utils/product_screen_util";
import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("CoopPosFullFlowTour", {
    steps: () =>
        [
            Chrome.startPoS(),
            Dialog.confirm("Open Register"),

            ProductScreen.clickDisplayedProduct("Letter Tray", true, "1.0", "4.80"),

            {
                content: "Click on the orderline to select it",
                trigger: ".orderline .product-name:contains('Letter Tray')",
                run: "click",
            },

            Numpad.click("0"),

            ProductScreen.orderIsEmpty(),

            ProductScreen.clickDisplayedProduct("Letter Tray", true, "1.0", "4.80"),

            ProductScreen.clickPayButton(),

            PaymentScreen.clickPaymentMethod("Cash"),

            {
                content: "Check for Verify Payment Dialog or proceed",
                trigger: ".modal-body, .paymentlines",
                run: function () {
                    const dialog = document.querySelector(".modal-body");
                    if (dialog) {
                        const confirmButton = document.querySelector(
                            ".modal-footer .btn-primary"
                        );
                        if (confirmButton) {
                            confirmButton.click();
                        }
                    }
                },
            },

            {
                content: "Wait for dialog to close and payment line to be added",
                trigger: ".paymentlines .paymentline",
            },

            PaymentScreen.clickPaymentMethod("Cash"),

            {
                content: "Check for duplicate journal error",
                trigger:
                    ".modal-body:contains('A payment line with the same Account Journal already exists.')",
                run: function () {
                    const dialog = document.querySelector(".modal-body");
                    if (dialog && dialog.textContent.includes("same Account Journal")) {
                        const okButton = document.querySelector(
                            ".modal-footer .btn-primary"
                        );
                        if (okButton) {
                            okButton.click();
                        }
                    }
                },
            },

            {
                content: "Wait for error dialog to close",
                trigger: ".payment-screen",
            },

            PaymentScreen.clickValidate(),
        ].flat(),
});
