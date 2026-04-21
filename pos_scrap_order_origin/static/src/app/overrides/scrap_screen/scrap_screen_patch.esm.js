// Copyright (C) Trobz (<https://trobz.com/>)
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import {onWillStart, useState} from "@odoo/owl";
import {AlertDialog} from "@web/core/confirmation_dialog/confirmation_dialog";
import {ScrapScreen} from "@pos_scrap_order/app/screens/scrap_screen/scrap_screen.esm";
import {_t} from "@web/core/l10n/translation";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";

patch(ScrapScreen.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.originState = useState({
            selectedReasonTagId: null,
            reasonTags: [],
        });
        onWillStart(async () => {
            await this._loadReasonTags();
        });
    },

    async _loadReasonTags() {
        const configTagIds = this.pos.config.raw?.scrap_reason_tag_ids || [];
        if (!configTagIds.length) return;
        this.originState.reasonTags = await this.orm.searchRead(
            "stock.scrap.reason.tag",
            [["id", "in", configTagIds]],
            ["name"]
        );
    },

    selectReasonTag(id) {
        this.originState.selectedReasonTagId = id;
    },

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

        const defaultVals = {
            scrap_reason_tag_id: this.originState.selectedReasonTagId,
        };

        try {
            const result = await this.pos.data.call(
                "pos.order",
                "create_scrap_from_ui",
                [orderData, defaultVals]
            );
            const {scrap_ids, msg} = result;
            if (msg && msg.title) {
                this.dialog.add(AlertDialog, {
                    title: msg.title,
                    body: msg.body,
                });
            }
            if (scrap_ids && scrap_ids.length > 0) {
                this.pos.add_new_order();
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
    },
});
