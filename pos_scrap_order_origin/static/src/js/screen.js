/* Copyright (C) Nguyen Minh Chien (chien@trobz.com)
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

odoo.define("pos_scrap_order_origin.screens", function (require) {
    "use strict";
    var rpc = require("web.rpc");
    var gui = require("point_of_sale.gui");
    var scrapScreens = require("pos_scrap_order.screens");
    var core = require("web.core");
    var session = require("web.session");
    var QWeb = core.qweb;

    scrapScreens.ScrapScreenWidget.include({
        selectOrigin: function ($el) {
            $(this.el).find(".origin").removeClass("active");
            $el.addClass("active");
        },
        _get_vals: function (order_vals) {
            if (this.pos.config.scrap_origin_ids.length === 0) {
                this.gui.show_popup("error", {
                    title: _t("Pas d'origine"),
                    body: _t("Veuillez configurer l'origine du rebut dans le backend."),
                });
            } else {
                var order_vals = this._super(order_vals);
                var origin = $(this.el).find(".origin.active");
                if (origin.length < 1) {
                    this.gui.show_popup("error", {
                        title: _t("Pas d'origine"),
                        body: _t("Veuillez sélectionnez l'origine."),
                    });
                } else {
                    var origin_id = parseInt(origin.attr("data-id"));
                    order_vals.scrap_origin_id = origin_id;
                    return order_vals;
                }
            }
        },
        renderElement: function () {
            var self = this;
            this._super();
        },

        render_scrap: function () {
            this._super();
            self = this;
            var scrapOrigins = _.filter(self.pos.scrap_origins, function (origin) {
                return self.pos.config.scrap_origin_ids.includes(origin.id);
            });
            this.$(".pos-scrap-left-container").html(
                QWeb.render("ScrapScreen-Origins", {scrapOrigins: scrapOrigins})
            );
            this.$(".origin").click(function () {
                self.selectOrigin($(this));
            });
        },
    });
});
