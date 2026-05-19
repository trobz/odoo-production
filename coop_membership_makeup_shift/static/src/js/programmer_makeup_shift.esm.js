import publicWidget from "@web/legacy/js/public/public_widget";
import {rpc} from "@web/core/network/rpc";

publicWidget.registry.programmer_makeup_shift = publicWidget.Widget.extend({
    selector: ".programmer_makeup_shift",

    start() {
        const self = this;

        $(".fa.fa-user-plus").on("click", function () {
            const shift_id = $(this).attr("data-shift-id");
            self.shift_id = shift_id;
            $("#modal_time").text($(`#time-${shift_id}`).text());
            $("#modal_hour").text($(`#hour-${shift_id}`).text());
        });

        $(".fa.fa-check").on("click", async function (e) {
            e.preventDefault();
            const btn_check = this;
            $(btn_check).attr("disabled", "disabled");
            const showError = (header, body) => {
                $("#error_header").text(header || "");
                $("#error_body").text(body || "");
                (window.Modal || window.bootstrap?.Modal)
                    ?.getInstance(document.getElementById("programmer_modal"))
                    ?.hide();
                new (window.Modal || window.bootstrap?.Modal)(
                    document.getElementById("error_modal")
                ).show();
            };
            try {
                const resp = await rpc("/web/dataset/call_kw", {
                    model: "shift.shift",
                    method: "register_makeup_shift",
                    args: [[parseInt(self.shift_id, 10)]],
                    kwargs: {},
                });
                const code = resp[0];
                const msg = resp[1];
                if (code === 1) {
                    $(`#btn-add-${self.shift_id}`)
                        .removeAttr("data-bs-toggle")
                        .removeAttr("data-bs-target")
                        .css({color: "grey"});
                    const $seats = $(`#avalable-seats-${self.shift_id}`);
                    $seats.text(parseInt($seats.text(), 10) - 1);
                    (window.Modal || window.bootstrap?.Modal)
                        ?.getInstance(document.getElementById("programmer_modal"))
                        ?.hide();
                } else if (msg) {
                    showError("", msg);
                }
            } catch (err) {
                showError(err.message || "", (err.data && err.data.message) || "");
            } finally {
                $(btn_check).removeAttr("disabled");
            }
        });
    },
});
