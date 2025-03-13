

odoo.define("pos_pricelist_selection_right.screens", function (require) {
    "use strict";

    var screens = require("point_of_sale.screens");

    screens.set_pricelist_button.include({

        /* Overwrite button_click function to remove technical pricelist
        */
        button_click: function () {
            var self = this;

            /*Begin of the changes */
            var pricelists = _.filter(self.pos.pricelists, function(pricelist) {
                return (
                    pricelist.id === self.pos.get_order().get_client().property_product_pricelist[0]
                );
            });
            if (pricelists.length === 0) {
                pricelists = _.filter(self.pos.pricelists, function(pricelist) {
                    return (
                        pricelist.id === self.pos.default_pricelist.id
                    );
                });
            }
            /*End of the changes */

            pricelists = _.map(pricelists, function (pricelist) {
                return {
                    label: pricelist.name,
                    item: pricelist
                };
            });

            self.gui.show_popup("selection",{
                title: _t("Select pricelist"),
                list: pricelists,
                confirm: function (pricelist) {
                    var order = self.pos.get_order();
                    order.set_pricelist(pricelist);
                },
                is_selected: function (pricelist) {
                    return pricelist.id === self.pos.get_order().pricelist.id;
                }
            });
        },

    });
});