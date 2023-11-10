odoo.define('foodcoop_data_role.AccessButtons', function(require) {
    "use strict";

    var core = require('web.core');
    var session = require('web.session');
    var ListRenderer = require('web.ListRenderer');
    var FormRenderer = require('web.FormRenderer');

    FormRenderer.include({

        hide_button: function(result) {
            this._super.apply(this, arguments);
            if (result.result == 'saisie_group_partner') {
                // Hide all buttons excepts "Print"
                var btns = self.$('.o_cp_sidebar > .btn-group >.o_dropdown');
                _.each(btns, function(btn){
                    var $btn = $(btn);
                    if ($btn.find('[data-section=print]').length == 0){
                        $btn.hide();
                    }
                })
            }
        }
    });

    ListRenderer.include({

        hide_button_select: function(result) {
            this._super.apply(this, arguments);
            if (result.result === 'saisie_group_partner'){
                // Hide all buttons excepts "Print"
                var btns = self.$('.o_cp_sidebar > .btn-group >.o_dropdown');
                _.each(btns, function(btn){
                    var $btn = $(btn);
                    if ($btn.find('[data-section=print]').length == 0){
                        $btn.hide();
                    }
                })
            }
        },
    })

});
