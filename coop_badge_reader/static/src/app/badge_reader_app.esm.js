import {App, Component, useState, whenReady} from "@odoo/owl";
import {makeEnv, startServices} from "@web/env";
import {MainComponentsContainer} from "@web/core/main_components_container";
import {PartnerFormComponent} from "@coop_badge_reader/components/partner_form/partner_form.esm";
import {PartnerListComponent} from "@coop_badge_reader/components/partner_list/partner_list.esm";
import {_t} from "@web/core/l10n/translation";
import {getTemplate} from "@web/core/templates";
import {session} from "@web/session";
import {url} from "@web/core/utils/urls";
import {useService} from "@web/core/utils/hooks";

class badgeReaderApp extends Component {
    static template = "coop_badge_reader.badge_reader_app";
    static props = {
        companyId: {type: Number},
        companyName: {type: String},
    };
    static components = {
        MainComponentsContainer,
        PartnerFormComponent,
        PartnerListComponent,
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.ui = useService("ui");
        this.companyImageUrl = url("/web/binary/company_logo", {
            company: this.props.companyId,
        });
        this.state = useState({
            active_display: "main",
            previous_display: "main",
        });
        this.partners = useState({
            partnerIds: [],
            selectedPartnerId: null,
        });
        this.searchValue = useState({
            barcode: "",
            barcode_base: "",
            partner_name: "",
        });
        this.errorMessage = useState({
            message: "",
        });
    }

    get attributesFieldsSearch() {
        return {
            barcode: {
                label: _t("Barcode"),
                value: this.searchValue.barcode,
                placeholder: _t("Scan or enter barcode"),
            },
            barcode_base: {
                label: _t("Member number"),
                value: this.searchValue.barcode_base,
                placeholder: _t("Scan or enter member number"),
            },
            partner_name: {
                label: _t("Name"),
                value: this.searchValue.partner_name,
                placeholder: _t("Enter name"),
            },
        };
    }

    get selectedPartnerId() {
        return this.partners.selectedPartnerId;
    }

    get partnerIds() {
        return this.partners.partnerIds;
    }

    get displayBackButton() {
        return this.state.active_display !== "main";
    }

    onInputSearch(fieldName, ev) {
        this.searchValue[fieldName] = ev.target.value;
    }

    async onSearch() {
        if (this.searchValue.barcode !== "") {
            const partnerIds = await this._searchByBarcode(this.searchValue.barcode);
            this._renderSearchResults("barcode", partnerIds);
        } else if (this.searchValue.barcode_base !== "") {
            const partnerIds = await this._searchByBarcodeBase(
                this.searchValue.barcode_base
            );
            this._renderSearchResults("barcode_base", partnerIds);
        } else if (this.searchValue.partner_name !== "") {
            const partnerIds = await this._searchByName(this.searchValue.partner_name);
            this._renderSearchResults("partner_name", partnerIds);
        } else {
            this.errorMessage.message = _t("Please enter a search value");
        }
    }

    onSelectPartner(partnerId) {
        // Function called when we click on a partner in the partner list,
        // we want to display the partner form
        this.state.previous_display = "partner_list";
        this.setPartnerSelected(partnerId);
        this.switchDisplay("partner_form");
    }

    onClickBack() {
        this.switchDisplay(this.state.previous_display);
    }

    _playSound(soundId) {
        const sound = document.getElementById(soundId);
        if (sound) {
            sound.play().catch(() => {
                return;
            });
        }
    }

    _renderSearchResults(searchType, partnerIds) {
        if (partnerIds.length === 0) {
            this._searchNotFound(searchType);
        } else if (partnerIds.length === 1) {
            this.resetSearch();
            this.setPartnerSelected(partnerIds[0]);
            this.switchDisplay("partner_form");
        } else {
            this.resetSearch();
            this.setPartnerIds(partnerIds);
            this.switchDisplay("partner_list");
        }
    }

    _searchNotFound(searchType) {
        if (searchType === "barcode") {
            this.errorMessage.message = _t("Barcode incorrect");
        }
        if (searchType === "barcode_base") {
            this.errorMessage.message = _t("Member number incorrect");
        }
        if (searchType === "partner_name") {
            this.errorMessage.message = _t("No partner found with this name");
        }
        this._playSound("sound_res_partner_not_found");
    }

    async _searchByBarcode(barcode) {
        const partners = await this.orm.searchRead(
            "res.partner",
            [
                ["is_deceased", "=", false],
                ["barcode", "=", barcode],
                "|",
                ["is_associated_people", "=", true],
                ["is_member", "=", true],
            ],
            ["id"]
        );
        return partners.map((p) => p.id);
    }

    async _searchByBarcodeBase(barcodeBase) {
        const partners = await this.orm.searchRead(
            "res.partner",
            [
                ["is_deceased", "=", false],
                ["barcode_base", "=", barcodeBase],
                "|",
                ["is_associated_people", "=", true],
                ["is_member", "=", true],
            ],
            ["id"]
        );
        return partners.map((p) => p.id);
    }

    async _searchByName(name) {
        const partners = await this.orm.call("res.partner", "name_search", [
            name,
            [
                ["is_deceased", "=", false],
                "|",
                ["is_associated_people", "=", true],
                ["is_member", "=", true],
            ],
        ]);
        return partners.map((p) => p[0]) || [];
    }

    switchDisplay(next_screen) {
        const allowed = ["main", "partner_list", "partner_form"];
        if (!allowed.includes(next_screen)) {
            this.resetSearch();
            this.clearResults();
            this.state.previous_display = "main";
            this.state.active_display = "main";
            return;
        }
        const {active_display, previous_display} = this.state;
        if (active_display === "partner_list" && previous_display === "partner_form") {
            this.resetSearch();
            this.clearResults();
            this.state.previous_display = "main";
            this.state.active_display = "main";
            return;
        }
        this.state.previous_display = active_display;
        this.state.active_display = next_screen;
    }

    setPartnerSelected(partnerId) {
        this.partners.selectedPartnerId = partnerId;
    }

    setPartnerIds(partnerIds) {
        this.partners.partnerIds = partnerIds;
    }

    resetSearch() {
        this.searchValue.barcode = "";
        this.searchValue.barcode_base = "";
        this.searchValue.partner_name = "";
        this.errorMessage.message = "";
    }

    clearResults() {
        this.setPartnerIds([]);
        this.setPartnerSelected(null);
    }
}

export async function createBadgeReaderApp(document, badge_reader_info) {
    await whenReady();
    const env = makeEnv();
    await startServices(env);
    session.server_version_info = badge_reader_info.server_version_info;
    const app = new App(badgeReaderApp, {
        getTemplate,
        env: env,
        props: {
            companyId: badge_reader_info.company_id,
            companyName: badge_reader_info.company_name,
        },
        translateFn: _t,
        translatableAttributes: ["data-tooltip"],
    });
    return app.mount(document.body);
}

export default {badgeReaderApp, createBadgeReaderApp};
