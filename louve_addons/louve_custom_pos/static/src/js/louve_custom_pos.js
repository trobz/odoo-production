/*
Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
@author: Sylvain LE GAL (https://twitter.com/legalsylvain)
License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
*/


odoo.define('louve_custom_pos.louve_custom_pos', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var gui = require('point_of_sale.gui');
    var keyboard = require('point_of_sale.keyboard');
    var _t = core._t;

/* ********************************************************
Overload screens.ClientListScreenWidget
******************************************************** */
    screens.ClientListScreenWidget.include({
        partner_icon_url: function(id){
            return '/web/image?model=res.partner&id='+id+'&field=image';
        },
    });

/**********************************************************
Overload keyboard.OnscreenKeyboardWidget to show numeric keyboard 
**********************************************************/
    keyboard.OnscreenKeyboardWidget.include({
        connect : function(target){
            var self = this;
            this.$target = $(target);
            var parent_ele = $(this.$target).parent();
            this.$target.focus(function(){
                if ($(parent_ele).hasClass('numeric_keyboard')){
                    $('.simple_keyboard').hide();
                    $('.numeric_keyboard').show();
                }
                else{
                    $('.keyboard_frame  .simple_keyboard').show();
                    $('.keyboard_frame  .numeric_keyboard').hide();
                }
                // Assign this target input to widget.
                self.$target = $(this);
                self.show();
             });
        },
    });
});
