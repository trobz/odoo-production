import {Component, onWillStart} from "@odoo/owl";
import {_t} from "@web/core/l10n/translation";
import {useService} from "@web/core/utils/hooks";

export class PartnerListComponent extends Component {
    static template = "coop_badge_reader.PartnerList";
    static props = {
        displayBackButton: {type: Boolean},
        partnerIds: {type: Array},
        onSelectPartner: {type: Function},
        onClickBack: {type: Function},
    };

    setup() {
        this.notification = useService("notification");
        this.orm = useService("orm");
        onWillStart(async () => {
            this.partners = await this.loadPartners();
        });
    }

    async _loadPartnersInfos(partnerIds) {
        return await this.orm.searchRead(
            "res.partner",
            [["id", "in", partnerIds]],
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
                "error_message",
            ]
        );
    }

    async loadPartners() {
        const partnerIds = this.props.partnerIds || [];
        if (!partnerIds || partnerIds.length === 0) {
            return [];
        }
        const partners = await this._loadPartnersInfos(partnerIds);
        partners.forEach((partner) => {
            partner.image_url = `/web/image?model=res.partner&id=${partner.id}&field=image_1920`;
        });
        return partners;
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
}
