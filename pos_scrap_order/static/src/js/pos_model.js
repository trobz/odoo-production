/* Copyright (C) Nguyen Minh Chien (chien@trobz.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html
*/

odoo.define("pos_scrap_order.pos_model", function (require) {
    "use strict";
    var pos_model = require("point_of_sale.models");
    pos_model.load_fields("pos.config", ["scrap_order_option"]);
});
