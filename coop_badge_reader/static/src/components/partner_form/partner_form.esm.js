import {Component, onWillStart, useState} from "@odoo/owl";
import {_t} from "@web/core/l10n/translation";
import {useService} from "@web/core/utils/hooks";

export class PartnerFormComponent extends Component {
    static template = "coop_badge_reader.PartnerForm";
    static props = {
        displayBackButton: {type: Boolean},
        onClickBack: {type: Function},
        selectedPartnerId: {type: Number},
    };

    setup() {
        this.orm = useService("orm");
        this.message = useState({
            warning: "",
            fail: "",
            contact_us: "",
        });
        onWillStart(async () => {
            this.partner = await this.loadPartner();
        });
    }

    async _loadPartnerInfos(selectedPartnerId) {
        return await this.orm.searchRead(
            "res.partner",
            [["id", "=", selectedPartnerId]],
            [
                "id",
                "name",
                "street",
                "street2",
                "zip",
                "city",
                "customer",
                "country_id",
                "phone",
                "mobile",
                "bootstrap_cooperative_state",
                "cooperative_state",
                "display_name",
                "badge_to_distribute",
                "contact_us_message",
                "error_message",
            ]
        );
    }

    async loadPartner() {
        const partnerId = this.props.selectedPartnerId;
        if (!partnerId) return false;
        const graceResult = await this.orm.call("res.partner", "action_grace_partner", [
            partnerId,
        ]);
        const partners = await this._loadPartnerInfos(partnerId);
        if (!partners || partners.length === 0) {
            return;
        }
        const partner = partners[0];

        partner.image_url = `/web/image?model=res.partner&id=${partnerId}&field=image_1920`;
        partner.css_class = "partner-" + partner.bootstrap_cooperative_state;
        if (partner.error_message) {
            partner.css_class = "partner-error";
        }
        this._playSound(partner);
        if (partner.contact_us_message) {
            this.message.contact_us = partner.contact_us_message;
        }
        if (partner.cooperative_state === "delay" && graceResult) {
            const dateStopStr =
                graceResult.slice(8, 10) +
                "/" +
                graceResult.slice(5, 7) +
                "/" +
                graceResult.slice(0, 4);
            this.message.warning = _t(
                "A grace period until %s or until your next service has been assigned to you." +
                    "You may proceed with your shopping!",
                dateStopStr
            );
        } else if (partner.cooperative_state === "suspended") {
            this.message.fail = _t(
                "We were unable to grant you a grace period; " +
                    "you must make up your services before doing your shopping."
            );
        }
        return partner;
    }

    async onPartnerIn() {
        await this.orm.call("res.partner", "log_move", [this.partner.id, "in"]);
        window.location = this._redirectTo();
    }

    async onPartnerOut() {
        await this.orm.call("res.partner", "log_move", [this.partner.id, "out"]);
        window.location = this._redirectTo();
    }

    async onPartnerWrong() {
        await this.orm.call("res.partner", "log_move", [this.partner.id, "wrong"]);
        window.location = this._redirectTo();
    }

    async onSetBadgeDistributed() {
        await this.orm.call("res.partner", "set_badge_distributed", [this.partner.id]);
        window.location = this._redirectTo();
    }

    getCooperativeStateClass(state) {
        const stateClasses = {
            up_to_date: "label-success",
            alert: "label-warning",
            delay: "label-warning",
            suspended: "label-danger",
            not_concerned: "label-danger",
            blocked: "label-danger",
            unpayed: "label-danger",
            unsubscribed: "label-danger",
            exempted: "label-success",
            vacation: "label-danger",
        };
        return stateClasses[state] || "label-default";
    }

    getCooperativeStateLabel(state) {
        const stateLabels = {
            up_to_date: _t("Up to date"),
            alert: _t("Alert"),
            delay: _t("Grace period granted"),
            suspended: _t("Suspended"),
            not_concerned: _t("Not concerned"),
            blocked: _t("Blocked"),
            unpayed: _t("Unpaid"),
            unsubscribed: _t("Unsubscribed"),
            exempted: _t("Exempted"),
            vacation: _t("On leave"),
        };
        return stateLabels[state] || state;
    }

    _redirectTo() {
        const url = new URL("/badge_reader", window.location.origin);
        const currentParams = new URLSearchParams(window.location.search);
        currentParams.forEach((value, key) => {
            url.searchParams.set(key, value);
        });
        return url.toString();
    }

    _playSound(partner) {
        const soundId = "sound_res_partner_" + partner.bootstrap_cooperative_state;
        const sound = document.getElementById(soundId);
        if (sound) {
            sound.play().catch(() => {
                return;
            });
        }
    }
}
