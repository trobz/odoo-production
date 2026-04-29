import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { patch } from "@web/core/utils/patch";
import { onMounted } from "@odoo/owl";
import { loadPending, savePending } from "./pos_store.esm";

patch(ReceiptScreen.prototype, {
    setup() {
        super.setup();
        onMounted(async () => {
            try {
                const imageData = await this.generateTicketImage();
                if (!imageData) return;
                const uuid = this.currentOrder.uuid;
                try {
                    await this.pos.data.call("pos.order", "add_image_receipt", [uuid, imageData]);
                } catch {
                    const pending = loadPending();
                    if (!pending.find((r) => r.uuid === uuid)) {
                        pending.push({ uuid, data: imageData });
                        savePending(pending);
                    }
                }
            } catch (e) {
                console.error("[pos_receipt_attachment] capture failed:", e);
            }
        });
    },
});
