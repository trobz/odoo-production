import {loadPending, savePending} from "./pos_store.esm";
import {OrderReceipt} from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import {ReceiptScreen} from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import {onMounted} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";

patch(ReceiptScreen.prototype, {
    setup() {
        super.setup();
        onMounted(async () => {
            try {
                const imageData = await this._captureReceiptImage();
                if (!imageData) return;
                const uuid = this.currentOrder.uuid;
                try {
                    await this.pos.data.call("pos.order", "add_image_receipt", [
                        uuid,
                        imageData,
                    ]);
                } catch {
                    const pending = loadPending();
                    if (!pending.find((r) => r.uuid === uuid)) {
                        pending.push({uuid, data: imageData});
                        savePending(pending);
                    }
                }
            } catch (e) {
                console.error("[pos_receipt_attachment] capture failed:", e);
            }
        });
    },

    // The base64 logo is injected into receipt data via getReceiptHeaderData
    // (see pos_store.esm.js), so the template uses it as an inline src.
    // renderer.toJpeg handles everything — no manual DOM manipulation needed.
    async _captureReceiptImage() {
        return await this.renderer.toJpeg(
            OrderReceipt,
            {
                data: this.pos.orderExportForPrinting(this.pos.get_order()),
                formatCurrency: this.env.utils.formatCurrency,
                basic_receipt: false,
            },
            {addClass: "pos-receipt-print p-3"}
        );
    },
});
