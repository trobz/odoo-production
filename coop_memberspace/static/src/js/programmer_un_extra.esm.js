import publicWidget from "@web/legacy/js/public/public_widget";
import {rpc} from "@web/core/network/rpc";
import {session} from "@web/session";

export default publicWidget.registry.programmer_un_extra = publicWidget.Widget.extend({
    selector: ".programmer_un_extra",
    start() {
        const self = this;

        $(".fa.fa-user-plus").on("click", function () {
            const shift_id = $(this).attr("data-shift-id");
            self.shift_id = shift_id;
            $("#modal_time").text($(`#time-${shift_id}`).text());
            $("#modal_hour").text($(`#hour-${shift_id}`).text());
        });

        // eslint-disable-next-line complexity
        $(".fa.fa-check").on("click", async function (e) {
            e.preventDefault();
            const btn_check = this;
            $(btn_check).attr("disabled", "disabled");
            try {
                const resp = await rpc("/web/dataset/call_kw", {
                    model: "shift.shift",
                    method: "fetch_ftop_ticket",
                    args: [parseInt(self.shift_id, 10)],
                    kwargs: {},
                });
                const data = resp[0];
                const msg = resp[1];
                if (data.length > 0) {
                    const vals = {
                        state: "draft",
                        partner_id: parseInt(session.partner_id, 10),
                        shift_id: parseInt(self.shift_id, 10),
                        shift_ticket_id: parseInt(data[0], 10),
                        related_extension_id: false,
                    };
                    try {
                        await rpc("/web/dataset/call_kw", {
                            model: "shift.registration",
                            method: "create",
                            args: [[vals]],
                            kwargs: {},
                        });
                        $(`#btn-add-${self.shift_id}`)
                            .removeAttr("data-bs-toggle")
                            .removeAttr("data-bs-target")
                            .css({color: "grey"});
                        const $seats = $(`#avalable-seats-${self.shift_id}`);
                        $seats.text(parseInt($seats.text(), 10) - 1);
                        (window.Modal || window.bootstrap?.Modal)
                            ?.getInstance(document.getElementById("programmer_modal"))
                            ?.hide();
                    } catch (error) {
                        $("#error_header").text(error.message || "");
                        $("#error_body").text(
                            (error.data &&
                                error.data.arguments &&
                                error.data.arguments[0]) ||
                                ""
                        );
                        (window.Modal || window.bootstrap?.Modal)
                            ?.getInstance(document.getElementById("programmer_modal"))
                            ?.hide();
                        new (window.Modal || window.bootstrap?.Modal)(
                            document.getElementById("error_modal")
                        ).show();
                    }
                } else if (msg) {
                    $("#error_body").text(msg);
                    (window.Modal || window.bootstrap?.Modal)
                        ?.getInstance(document.getElementById("programmer_modal"))
                        ?.hide();
                    new (window.Modal || window.bootstrap?.Modal)(
                        document.getElementById("error_modal")
                    ).show();
                }
            } finally {
                $(btn_check).removeAttr("disabled");
            }
        });
    },
});
