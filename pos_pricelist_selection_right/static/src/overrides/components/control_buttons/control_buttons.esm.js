import {ControlButtons} from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import {patch} from "@web/core/utils/patch";

patch(ControlButtons.prototype, {
    /**
     * Restrict the pricelist selection popup to the pricelist assigned to the
     * current customer (``property_product_pricelist``). When the customer has
     * no pricelist assigned - or when no customer is set - fall back to the
     * shop's default pricelist (``pos.config.pricelist_id``).
     *
     * @override
     * @returns {Array}
     */
    getPricelistList() {
        const selectionList = super.getPricelistList();

        const partner = this.currentOrder.get_partner();
        const partnerPricelistId = partner?.property_product_pricelist?.id;
        const defaultPricelistId = this.pos.config.pricelist_id?.id;

        let restricted = selectionList.filter(
            (entry) => entry.item && entry.item.id === partnerPricelistId
        );
        if (restricted.length === 0) {
            restricted = selectionList.filter(
                (entry) => entry.item && entry.item.id === defaultPricelistId
            );
        }
        return restricted;
    },
});
