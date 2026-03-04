import {useEffect, useRef} from "@odoo/owl";
import {Chatter} from "@mail/chatter/web_portal/chatter";
import {patch} from "@web/core/utils/patch";

patch(Chatter.prototype, {
    setup() {
        super.setup(...arguments);
        this.topRef = useRef("top");
        useEffect(
            (el) => {
                if (el && this.env.chatter?.forceHideMailChatterTop) {
                    // Hide top ref
                    el.classList.add("d-none");
                }
            },
            () => [this.topRef.el]
        );
    },
});
