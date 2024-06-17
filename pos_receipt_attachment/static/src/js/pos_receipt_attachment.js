/** ****************************************************************************
    Copyright (C) Nguyen Minh Chien (chien@trobz.com)
    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 *****************************************************************************/

odoo.define("pos_receipt_attachment.models", function(require) {
    "use strict";
    var core = require('web.core');
    var models = require("point_of_sale.models");
    var rpc = require('web.rpc');

    var PosModelParent = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        _save_to_server: function(orders, options) {
            var self = this;
            var done = PosModelParent._save_to_server.apply(this, arguments);
            done.then(function(){
                var receipts = self.db.load('receipt_images', []);
                if (receipts.length > 0){
                    rpc.query({
                        model: 'pos.order',
                        method: 'add_image_receipt_patch',
                        args: [receipts]
                    })
                    .then(function (res) {
                        if (res){
                            self.db.save('receipt_images', []);
                        }
                    });                    
                }
            });
            return done
        },
    });
});
