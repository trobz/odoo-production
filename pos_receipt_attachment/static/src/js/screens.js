/* global html2canvas */
odoo.define('pos_receipt_attachment.screens', function (require) {
    "use strict";

    var screens = require('point_of_sale.screens');
    var rpc = require('web.rpc');

    screens.ReceiptScreenWidget.include({
        render_receipt: function(){
            this.receipt_order = this.pos.get_order();
            this._super();
        },
        handle_auto_print: function(){
            var self = this;
            var args = arguments;
            var _super = this._super;
            this.htmlToImg().then(function(receiptImage){
                // self._super();
                _super.apply(self, args);
                self.sendReceiptImage(receiptImage);
            });
        },
        sendReceiptImage: function(receiptImage){
            var done = new $.Deferred();
            if (this.receipt_order === undefined){
                done.reject()
            }
            const order = this.receipt_order;
            const orderName = order.get_name();
            var done = new $.Deferred();
            var self = this;
            rpc.query({
                model: 'pos.order',
                method: 'add_image_receipt',
                args: [orderName, receiptImage]
            })
            .fail(function (error) {
                // Connection error
                self.saveReceiptImage(orderName, receiptImage)
            });
            done.resolve(); 
            return done;
        },
        saveReceiptImage: function(orderName, receiptImage){
            var self = this;
            var receipts = self.pos.db.load('receipt_images', []);
            receipts.push({id: orderName, data: receiptImage});
            self.pos.db.save('receipt_images', receipts);
        },
        /**
         * Generate a jpeg image from a canvas
         * @param {DOMElement} canvas
         */
        process_canvas: function (canvas) {
            return canvas.toDataURL('image/jpeg').replace('data:image/jpeg;base64,','');
        },

        htmlToImg: function () {
            var self = this;
            var receipt = $('.pos-receipt-container>.pos-sale-ticket');
            var promise = new Promise(function (resolve, reject) {
                html2canvas(receipt[0], {
                    onparsed: function(queue) {
                        queue.stack.ctx.height = Math.ceil(receipt.outerHeight() + receipt.offset().top);
                        queue.stack.ctx.width = Math.ceil(receipt.outerWidth() + 2 * receipt.offset().left);
                    },
                    onrendered: function (canvas) {
                        resolve(self.process_canvas(canvas));
                    },
                    letterRendering: false,
                })
            });
            return promise;
        },
    
    });

});
