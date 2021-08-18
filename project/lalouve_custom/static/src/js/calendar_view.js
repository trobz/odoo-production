odoo.define('lalouve_custom.CalendarView', function (require) {
    "use strict";

    var CalendarView = require('web.CalendarView');

    CalendarView.include({
        init: function (viewInfo, params) {
            this._super.apply(this, arguments);
            for (const fieldName in this.loadParams.filters){
                if (fieldName == 'partner_ids'){
                    this.loadParams.filters[fieldName].all = true;
                }
            }
        },
    });

});
