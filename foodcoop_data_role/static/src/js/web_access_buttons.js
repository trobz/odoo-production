odoo.define('foodcoop_data_role.AccessButtons', function(require) {
    "use strict";

    var core = require('web.core');
    var session = require('web.session');
    var ListRenderer = require('web.ListRenderer');
    var FormRenderer = require('web.FormRenderer');

    FormRenderer.include({

        hide_button: function(result) {
            if (result == 'saisie_group_partner') {
                //self.$('.o_cp_sidebar').hide();
                self.$('.o_chatter_topbar').hide();
            } else {
                this._super.apply(this, arguments)
            }
        }
    });

    ListRenderer.include({

        hide_button_select: function(result) {
            if (result) {
                if (result === 'saisie_group_partner'){
                    var btns = self.$('.o_cp_sidebar > .btn-group >.o_dropdown');
                    _.each(btns, function(btn){
                        var $btn = $(btn);
                        if ($btn.find('[data-section=print]').length == 0){
                            $btn.hide();
                        }
                    })
                }
                else {
                    self.$('.o_cp_sidebar ').hide();
                }
            } else {
                self.$('.o_cp_sidebar').show();
            }
        },
    })

});
