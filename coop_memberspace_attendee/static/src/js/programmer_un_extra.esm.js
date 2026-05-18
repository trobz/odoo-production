import publicWidget from "@web/legacy/js/public/public_widget";
import {rpc} from "@web/core/network/rpc";

publicWidget.registry.programmer_un_extra.include({
    start() {
        this._super(...arguments);
        this.$el.on("click", ".browse-expected-attendee", async (e) => {
            const shiftId = parseInt($(e.currentTarget).attr("shift-id"), 10);
            const partners = await rpc("/web/dataset/call_kw", {
                model: "shift.shift",
                method: "get_expected_attendee",
                args: [[shiftId]],
                kwargs: {},
            });
            $(".modal_list_expected_attendee_body").empty();
            for (const partner of partners) {
                $(".modal_list_expected_attendee_body").append(
                    `<tr><td>${partner}</td></tr>`
                );
            }
        });
    },
});
