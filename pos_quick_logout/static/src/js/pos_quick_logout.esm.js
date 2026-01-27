/*
    Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
    Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
    @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
*/
import {onWillRender, useState} from "@odoo/owl";
import {ConfirmationDialog} from "@web/core/confirmation_dialog/confirmation_dialog";
import {Navbar} from "@point_of_sale/app/navbar/navbar";
import {_t} from "@web/core/l10n/translation";
import {patch} from "@web/core/utils/patch";
import {redirect} from "@web/core/utils/urls";

patch(Navbar.prototype, {
    setup() {
        super.setup();
        this.timer = false;
        this.showQuickLogout = useState({
            isVisible: false,
        });
        onWillRender(() => {
            this.renderElementLogout();
        });
    },

    onClickLogout() {
        this.dialog.add(ConfirmationDialog, {
            title: _t("Logout"),
            body: _t("Are you sure you want to logout?"),
            confirm: () => {
                redirect("/web/session/logout");
            },
        });
    },

    renderElementLogout() {
        const initialUserId = this.pos.session.user_id;
        if (!initialUserId || initialUserId.id !== this.pos.user.id) {
            this.showQuickLogout.isVisible = true;
        } else {
            this.showQuickLogout.isVisible = false;
        }
    },
});
