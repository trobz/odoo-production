import * as Chrome from "@point_of_sale/../tests/tours/utils/chrome_util";
import * as Dialog from "@point_of_sale/../tests/tours/utils/dialog_util";
import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("CoopCashInOutTour", {
    steps: () =>
        [
            Chrome.startPoS(),
            Dialog.confirm("Open Register"),
            Chrome.clickMenuButton(),
            Chrome.clickMenuDropdownOption("Cash In/Out"),
            {
                content: "Type a non-zero cash in amount",
                trigger: ".input-amount input",
                run: "edit 10",
            },
            Chrome.fillTextArea(".cash-reason", "Float"),
            Dialog.confirm(),
            {
                content: "Cash in succeeded (success notification shown)",
                trigger: ".o_notification:contains('Successfully made a cash')",
            },
            Chrome.endTour(),
        ].flat(),
});
