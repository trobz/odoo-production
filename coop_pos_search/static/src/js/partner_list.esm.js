import {PartnerList} from "@point_of_sale/app/screens/partner_list/partner_list";
import {patch} from "@web/core/utils/patch";
import {unaccent} from "@web/core/utils/strings";

patch(PartnerList.prototype, {
    get _queryAsNumber() {
        const normalized = unaccent(
            (this.state.query || "").trim(),
            false
        ).toLowerCase();
        const digits = normalized.replace(/[+\s()-]/g, "");
        return /^[0-9]+$/.test(digits) ? digits : null;
    },

    getPartners() {
        const numberString = this._queryAsNumber;
        if (numberString) {
            return this.pos.models["res.partner"]
                .getAll()
                .filter((partner) => partner.exactMatch(numberString));
        }
        return super.getPartners();
    },

    async getNewPartners() {
        const numberString = this._queryAsNumber;
        if (!numberString) {
            return await super.getNewPartners();
        }
        const searchFields = [...this.getPhoneSearchTerms(), "barcode", "barcode_base"];
        const domain = [
            ...Array(searchFields.length - 1).fill("|"),
            ...searchFields.map((field) => [
                field,
                "=",
                field === "barcode_base" ? Number(numberString) : numberString,
            ]),
            ["customer", "=", true],
        ];
        return await this.pos.data.searchRead("res.partner", domain, [], {
            limit: 1,
            offset: this.state.currentOffset,
        });
    },
});
