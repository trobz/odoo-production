import {PartnerList} from "@point_of_sale/app/screens/partner_list/partner_list";
import {patch} from "@web/core/utils/patch";
import {unaccent} from "@web/core/utils/strings";

// Only search by phone/mobile once the number query has at least this many digits.
const MIN_PHONE_SEARCH_LENGTH = 3;

patch(PartnerList.prototype, {
    get _queryAsNumber() {
        const normalized = unaccent(
            (this.state.query || "").trim(),
            false
        ).toLowerCase();
        const digits = normalized.replace(/[+\s()-]/g, "");
        return /^[0-9]+$/.test(digits) ? digits : null;
    },

    _filterPartners(partners) {
        return partners.filter((partner) => partner.customer && !partner.is_deceased);
    },

    getPartners() {
        const numberString = this._queryAsNumber;
        let partners = [];
        if (numberString) {
            partners = this.pos.models["res.partner"]
                .getAll()
                .filter((partner) => partner.exactMatch(numberString));
        } else partners = super.getPartners();
        return this._filterPartners(partners);
    },

    async getNewPartners() {
        const numberString = this._queryAsNumber;
        if (!numberString) {
            const partners = await super.getNewPartners();
            return this._filterPartners(partners);
        }
        const searchFields = [
            ...(numberString.length >= MIN_PHONE_SEARCH_LENGTH
                ? this.getPhoneSearchTerms()
                : []),
            "barcode",
            "barcode_base",
        ];
        const domain = [
            ...Array(searchFields.length - 1).fill("|"),
            ...searchFields.map((field) => [
                field,
                "=",
                field === "barcode_base" ? Number(numberString) : numberString,
            ]),
            ["customer", "=", true],
            ["is_deceased", "=", false],
        ];
        return await this.pos.data.searchRead("res.partner", domain, [], {
            limit: 1,
            offset: this.state.currentOffset,
        });
    },
});
