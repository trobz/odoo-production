import publicWidget from "@web/legacy/js/public/public_widget";
import {rpc} from "@web/core/network/rpc";

publicWidget.registry.cancelShiftRegistration = publicWidget.Widget.extend({
    selector: ".exchange-shift",

    start() {
        this._super(...arguments);

        this.$el.on("click", ".confirm-cancel-registration", (ev) => {
            this.registration_id = parseInt(
                $(ev.currentTarget).attr("registration-id"),
                10
            );
            const registration_name = $(ev.currentTarget).attr("registration-name");
            const target = $(ev.currentTarget).attr("data-bs-target");
            const $popup = $(target);
            if ($popup.length && $popup.find(".service_name").length) {
                $popup.find(".service_name").text(registration_name);
            }
        });

        $(".modal_confirm_cancel_registration").on(
            "click",
            ".cancel-registration",
            (ev) => {
                $(ev.currentTarget).off("click");
                rpc("/web/dataset/call_kw", {
                    model: "shift.registration",
                    method: "cancel_shift_regis_from_market",
                    args: [[this.registration_id]],
                    kwargs: {},
                }).then(() => {
                    window.location.reload();
                });
            }
        );
    },
});
