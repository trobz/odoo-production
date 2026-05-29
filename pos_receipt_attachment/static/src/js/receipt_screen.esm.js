import {loadPending, savePending} from "./pos_store.esm";
import {OrderReceipt} from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import {ReceiptScreen} from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import {htmlToCanvas} from "@point_of_sale/app/printer/render_service";
import {onMounted} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";

async function fetchBase64(url) {
    try {
        const res = await fetch(url);
        if (!res.ok) return null;
        const blob = await res.blob();
        return await new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
    } catch {
        return null;
    }
}

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

    async _captureReceiptImage() {
        const data = this.pos.orderExportForPrinting(this.pos.get_order());
        const el = await this.renderer.toHtml(OrderReceipt, {
            data,
            formatCurrency: this.env.utils.formatCurrency,
            basic_receipt: false,
        });

        const logoImg = el.querySelector("img.pos-receipt-logo");
        if (logoImg && logoImg.src && !logoImg.src.startsWith("data:")) {
            const base64 = await fetchBase64(logoImg.src);
            if (base64) {
                logoImg.src = base64;
                try {
                    await logoImg.decode();
                } catch {
                    // Decode() failure is non-fatal; canvas render proceeds with cached image
                }
            }
        }

        const canvas = await htmlToCanvas(el, {addClass: "pos-receipt-print p-3"});
        return canvas.toDataURL("image/jpeg").replace("data:image/jpeg;base64,", "");
    },
});
