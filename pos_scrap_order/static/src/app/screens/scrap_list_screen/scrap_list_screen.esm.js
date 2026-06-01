import {Component, onMounted, useState} from "@odoo/owl";
import {AlertDialog} from "@web/core/confirmation_dialog/confirmation_dialog";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {usePos} from "@point_of_sale/app/store/pos_hook";
import {useService} from "@web/core/utils/hooks";

export class ScrapListScreen extends Component {
    static template = "pos_scrap_order.ScrapListScreen";
    static props = {};
    static storeOnOrder = false;

    setup() {
        this.pos = usePos();
        this.dialog = useService("dialog");
        this.state = useState({scrapOrders: []});

        onMounted(async () => {
            try {
                this.state.scrapOrders = await this.pos.data.call(
                    "stock.scrap",
                    "get_list_for_ui",
                    []
                );
            } catch {
                this.dialog.add(AlertDialog, {
                    title: _t("Network Connection Lost"),
                    body: _t(
                        "It seems that you do not have a network connection at the moment. Try again later."
                    ),
                });
            }
        });
    }

    clickBack() {
        this.pos.showScreen("ProductScreen");
    }
}

registry.category("pos_screens").add("ScrapListScreen", ScrapListScreen);
