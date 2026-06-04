import {PosStore} from "@point_of_sale/app/store/pos_store";
import {patch} from "@web/core/utils/patch";

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
    async setup(...args) {
        await super.setup(...args);
        // Flush any receipt images that were saved offline in a previous session.
        // This covers the case where the server was unreachable during the receipt
        // screen (so no orphan attachment was created) and the browser was never
        // technically "offline" (so the "online" event never fired to re-trigger sync).
        this._flushPendingReceipts().catch(() => {});
    },

    // Called by syncAllOrders after each order is successfully synced.
    async postSyncAllOrders(...args) {
        await super.postSyncAllOrders(...args);
        await this._flushPendingReceipts();
    },

    async _flushPendingReceipts() {
        const pending = loadPending();
        if (!pending.length) return;
        const remaining = [];
        for (const receipt of pending) {
            try {
                await this.data.call("pos.order", "add_image_receipt", [
                    receipt.uuid,
                    receipt.data,
                ]);
            } catch {
                remaining.push(receipt);
            }
        }
        savePending(remaining);
    },
});
