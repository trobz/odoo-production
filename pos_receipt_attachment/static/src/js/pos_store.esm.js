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
        // Pre-fetch the company logo while online so it is available for receipt
        // image capture even when the device goes offline later.
        this._cacheCompanyLogo().catch(() => {
            // Intentionally ignore errors during background cache operation
        });
        // Flush any receipt images that were saved offline in a previous session.
        this._flushPendingReceipts().catch(() => {
            // Intentionally ignore errors during background flush operation
        });
    },

    async _cacheCompanyLogo() {
        if (this.company_logo_base64) return;
        const url = `/web/image?model=res.company&id=${this.company.id}&field=logo_web`;
        try {
            const res = await fetch(url);
            if (!res.ok) return;
            const blob = await res.blob();
            this.company_logo_base64 = await new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onloadend = () => resolve(reader.result);
                reader.onerror = reject;
                reader.readAsDataURL(blob);
            });
        } catch (e) {
            console.warn("[pos_receipt_attachment] Failed to cache company logo:", e);
        }
    },

    // Inject the pre-cached base64 logo into receipt data so the template can
    // use it as an inline src. html-to-image skips data-URI images (no re-fetch
    // needed), which avoids the library's broken cache-key bug (strips query
    // params, so all /web/image URLs share one cache slot).
    getReceiptHeaderData(order) {
        const result = super.getReceiptHeaderData(order);
        if (this.company_logo_base64) {
            result.company_logo = this.company_logo_base64;
        }
        return result;
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
