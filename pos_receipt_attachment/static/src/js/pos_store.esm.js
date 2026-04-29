import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

const STORAGE_KEY = "pos_receipt_images";

export function loadPending() {
    try {
        return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    } catch {
        return [];
    }
}

export function savePending(items) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
}

patch(PosStore.prototype, {
    // Called by syncAllOrders after each batch of orders is successfully synced.
    // Equivalent of v12's _save_to_server patch — flush offline receipt queue once
    // the server has confirmed the orders exist.
    async postSyncAllOrders(orders) {
        await super.postSyncAllOrders(...arguments);
        const pending = loadPending();
        if (!pending.length) return;
        const remaining = [];
        for (const receipt of pending) {
            try {
                await this.data.call("pos.order", "add_image_receipt", [receipt.uuid, receipt.data]);
            } catch {
                remaining.push(receipt);
            }
        }
        savePending(remaining);
    },
});
