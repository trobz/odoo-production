import {PosStore} from "@point_of_sale/app/store/pos_store";
import {_t} from "@web/core/l10n/translation";
import {ask} from "@point_of_sale/app/store/make_awaitable_dialog";
import {patch} from "@web/core/utils/patch";

patch(PosStore.prototype, {
    async pay() {
        if (this.config.require_product_scale) {
            const order = this.get_order();
            const lines = order.lines.filter(
                (line) =>
                    Number.isInteger(line.get_quantity()) && line.product_id.to_weight
            );
            if (lines.length > 0) {
                const productNames = lines
                    .map((line) => line.product_id.display_name)
                    .join(", ");
                const confirmed = await ask(this.env.services.dialog, {
                    title: _t(
                        "Attention: One or more items to be weighed show a round weight (1 kg, 2 kg, 3 kg…)"
                    ),
                    body:
                        _t("The product(s) may need to be weighted with scale: ") +
                        productNames +
                        ". " +
                        _t("Are you sure that you want to continue the payment?"),
                });
                if (!confirmed) {
                    return;
                }
            }
        }
        return super.pay(...arguments);
    },
});
