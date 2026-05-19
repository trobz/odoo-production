import {
    AlertDialog,
    ConfirmationDialog,
} from "@web/core/confirmation_dialog/confirmation_dialog";
import {PosStore} from "@point_of_sale/app/store/pos_store";
import {_t} from "@web/core/l10n/translation";
import {patch} from "@web/core/utils/patch";

patch(PosStore.prototype, {
    async setDiscountFromUI(line, val) {
        const discountCategories = this.config.discount_category_all_ids;
        const product = line.product_id;
        if (this.config.discount_by_category && discountCategories.length > 0) {
            const productCategId = product.categ_id.id;
            const discountCategoryIds = discountCategories.map((categ) => categ.id);
            if (discountCategoryIds.includes(productCategId)) {
                this.dialog.add(ConfirmationDialog, {
                    body: _t(
                        "Attention, you are applying %s% discount for the product %s.\n" +
                            "Are you sure that you would like to proceed it?",
                        val,
                        product.display_name
                    ),
                    confirm: () => {
                        return super.setDiscountFromUI(line, val);
                    },
                    cancel: () => {
                        return;
                    },
                });
            } else {
                this.dialog.add(AlertDialog, {
                    title: _t("Error"),
                    body: _t(
                        "This discount does not apply for the product %s",
                        product.display_name
                    ),
                });
            }
        } else {
            return super.setDiscountFromUI(line, val);
        }
    },
});
