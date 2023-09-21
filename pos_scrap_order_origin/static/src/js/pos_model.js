/* Copyright (C) Nguyen Minh Chien (chien@trobz.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html
*/


odoo.define('pos_scrap_order_origin.pos_model', function (require) {
    "use strict";
    var pos_model = require('point_of_sale.models');
    pos_model.load_fields("pos.config", ['scrap_origin_ids']);
    pos_model.load_models({
        model: 'stock.scrap.origin',
        fields: ['name'],
        domain: [],
        context: {'pos': true},
        loaded: function (self, origins) {
            self.scrap_origins = origins;
            self.scrap_origin_by_id = {};
            for (var x = 0; x < origins.length; x++) {
                self.scrap_origin_by_id[origins[x].id] = origins[x];
            }
        },
    });
});
