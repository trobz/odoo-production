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

        /**
         * Renders the html as an image to print it
         */
        htmlToImg: function () {
            var receipt = $('.pos-receipt-container>.pos-sale-ticket');
            // Odoo RTL support automatically flip left into right but html2canvas
            // won't work as expected if the receipt is aligned to the right of the
            // screen so we need to flip it back.
            receipt.parent().css({ left: 0, right: 'auto' });
            return html2canvas(receipt[0], {
                height: Math.ceil(receipt.outerHeight() + receipt.offset().top),
                width: Math.ceil(receipt.outerWidth() + receipt.offset().left),
                // width: Math.ceil(receipt.outerWidth()),
                scale: 1,
            }).then(canvas => {
                // $('.pos-receipt-print').empty();
                return this.process_canvas(canvas);
            });
        },
    });

});
