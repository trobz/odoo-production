import {AlertDialog} from "@web/core/confirmation_dialog/confirmation_dialog";
import {Component} from "@odoo/owl";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {usePos} from "@point_of_sale/app/store/pos_hook";
import {useService} from "@web/core/utils/hooks";

export class ScrapScreen extends Component {
    static template = "pos_scrap_order.ScrapScreen";
    static props = {};
    static storeOnOrder = false;

    setup() {
        this.pos = usePos();
        this.dialog = useService("dialog");
    }

    get order() {
        return this.pos.get_order();
    }

    get orderlines() {
        return this.order?.lines || [];
    }

    clickBack() {
        this.pos.showScreen("ProductScreen");
    }

    async makeScrap() {
        const order = this.order;
        if (!order || order.lines.length === 0) {
            this.dialog.add(AlertDialog, {
                title: _t("Not available"),
                body: _t("This order has been paid or has no line."),
            });
            return;
        }

        const orderData = {
            pos_session_id: this.pos.session.id,
            lines: order.lines.map((line) => [
                0,
                0,
                {
                    product_id: line.product_id.id,
                    qty: line.qty,
                },
            ]),
        };

        try {
            const result = await this.pos.data.call(
                "pos.order",
                "create_scrap_from_ui",
                [orderData]
            );
            const {scrap_ids, msg} = result;
            if (msg && msg.title) {
                this.dialog.add(AlertDialog, {
                    title: msg.title,
                    body: msg.body,
                });
            }
            if (scrap_ids && scrap_ids.length > 0) {
                this.pos.removeOrder(order, false);
                this.pos.showScreen("ProductScreen");
            }
        } catch {
            this.dialog.add(AlertDialog, {
                title: _t("Network Connection Lost"),
                body: _t(
                    "It seems that you do not have a network connection at the moment. Try again later."
                ),
            });
        }
    }
}

registry.category("pos_screens").add("ScrapScreen", ScrapScreen);
