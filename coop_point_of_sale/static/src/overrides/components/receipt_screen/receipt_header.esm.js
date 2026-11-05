import {PosStore} from "@point_of_sale/app/store/pos_store";
import {patch} from "@web/core/utils/patch";

// The POS emails/prints receipts by taking a client-side screenshot of the
// receipt DOM (html-to-image). The company logo is referenced by a remote URL
// (/web/image?...&field=logo), which html-to-image has to re-fetch and inline.
// That fetch fails intermittently and the empty result is then cached for the
// whole POS session, so the logo randomly disappears from the captured receipt.
//
// Fix: pre-cache the company logo as a base64 data-URI and inject it into the
// receipt header data. html-to-image copies data-URIs verbatim (no re-fetch),
// so the logo is always present on the captured receipt.
patch(PosStore.prototype, {
    async setup(...args) {
        await super.setup(...args);
        // Pre-fetch the company logo while online so it is available for the
        // receipt image capture even when the device goes offline later.
        this._cacheCompanyLogo().catch(() => {
            // Intentionally ignore errors during background cache operation
        });
    },

    async _cacheCompanyLogo() {
        if (this.company_logo_base64) {
            return;
        }
        const url = `/web/image?model=res.company&id=${this.company.id}&field=logo_web`;
        try {
            const res = await fetch(url);
            if (!res.ok) {
                return;
            }
            const blob = await res.blob();
            this.company_logo_base64 = await new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onloadend = () => resolve(reader.result);
                reader.onerror = reject;
                reader.readAsDataURL(blob);
            });
        } catch (e) {
            console.warn("[coop_point_of_sale] Failed to cache company logo:", e);
        }
    },

    // Inject the pre-cached base64 logo into the receipt header data so the
    // template can use it as an inline src.
    getReceiptHeaderData(order) {
        const result = super.getReceiptHeaderData(order);
        if (this.company_logo_base64) {
            result.company_logo = this.company_logo_base64;
        }
        return result;
    },
});
