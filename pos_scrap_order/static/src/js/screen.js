/* Copyright (C) Nguyen Minh Chien (chien@trobz.com)
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

odoo.define("pos_scrap_order.screens", function(require) {
    "use strict";
    var rpc = require('web.rpc');
    var gui = require('point_of_sale.gui');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var session = require('web.session');
    var QWeb = core.qweb;

    var ScrapScreenWidget = screens.ScreenWidget.extend({
        template: 'ScrapScreenWidget',
        show: function(){
            this._super();
            var self = this;
            this.render_scrap();
        },

        lock_screen: function(locked) {
            this._locked = locked;
            if (locked) {
                this.$('.next').removeClass('highlight');
            } else {
                this.$('.next').addClass('highlight');
            }
        },
        get_scrap_render_env: function() {
            var order = this.pos.get_order();
            return {
                widget: this,
                pos: this.pos,
                order: order,
                orderlines: order.get_orderlines(),
            };
        },
        _get_vals: function(order_vals){
            return order_vals;
        },
        make_scrap: function() {
            var self = this;
            var order = this.pos.get_order()
            if (order && !order.finalized && order.get_orderlines().length > 0) {
                var order_vals = this._get_vals(order.export_as_JSON());
                if (order_vals){
                    this.lock_screen(true);
                    var params = {
                        model: 'pos.order',
                        method: 'create_scrap_from_ui',
                        args: [order_vals],
                        kwargs: {context: session.user_context},
                    };
        
                    rpc.query(params)
                    .then(function({scrap_ids, msg}){
                        if (scrap_ids && scrap_ids.length > 0){
                            // self.pos.db.remove_unpaid_order(order);
                            order.finalize();
                        }
                        if(msg){
                            self.gui.show_popup("alert", {
                                "title": msg.title,
                                "body":  msg.body
                            });
                        }
                    })
                    .fail(function(error, event){
                        event.preventDefault();
                        self.gui.show_popup("error", {
                            "title": _t("Network Connection Lost"),
                            "body":  _t(
                                "It seems that you do not have a network connection at the moment." +
                                " Try again later."),
                            // "confirm": function() {
                            //     self.click_back();
                            // },
                        });
                    })
                    .always(function(){
                        self.lock_screen(false);
                    });
                }
            } else {
                self.gui.show_popup("error", {
                    "title": _t("Not available"),
                    "body":  _t(
                        "This order has been paid or has no line.")
                });
            }
        },
        click_next: function() {
            // this.pos.get_order().finalize();
        },
        click_back: function() {
            this.gui.show_screen("products");
        },
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.next').click(function(){
                if (!self._locked) {
                    self.make_scrap();
                }
            });
            this.$('.back').click(function(){
                if (!self._locked) {
                    self.click_back();
                }
            });
        },

        render_scrap: function() {
            this.$('.pos-scrap-container').html(QWeb.render('ScrapLines', this.get_scrap_render_env()));
        },
    });
    gui.define_screen({name:'scrap', widget: ScrapScreenWidget});
    
    var ScrapButton = screens.ActionButtonWidget.extend({
        template: 'ScrapButton',
        button_click: function() {
            if (this.pos.get_order() && this.pos.get_order().get_orderlines().length > 0) {
                this.gui.show_screen('scrap');
            } else {
                this.gui.show_popup('error', {
                    'title': _t('Nothing to Scrap'),
                    'body':  _t('There is no product to scrap.'),
                });
            }
        },
    });
    
    screens.define_action_button({
        'name': 'scrap',
        'widget': ScrapButton,
        'condition': function(){
            var opt = this.pos.config.scrap_order_option;
            return opt !== undefined && opt !== 'no';
        },
    });
    return {
        ScrapScreenWidget: ScrapScreenWidget,
    };
});
