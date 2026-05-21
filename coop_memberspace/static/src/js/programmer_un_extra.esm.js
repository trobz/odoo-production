import publicWidget from "@web/legacy/js/public/public_widget";
import {rpc} from "@web/core/network/rpc";

function bsModal(id) {
    const BS = window.Modal || window.bootstrap?.Modal;
    return BS
        ? {
              getInstance: () => BS.getInstance(document.getElementById(id)),
              create: () => new BS(document.getElementById(id)),
          }
        : null;
}

export default publicWidget.registry.programmer_un_extra = publicWidget.Widget.extend({
    selector: ".programmer_un_extra",

    _hideProgrammerModal() {
        bsModal("programmer_modal")?.getInstance()?.hide();
    },

    _showErrorModal(header, body) {
        this._hideProgrammerModal();
        $("#error_header").text(header || "");
        $("#error_body").text(body || "");
        bsModal("error_modal")?.create()?.show();
    },

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
            try {
                const [registration_id, , msg] = await rpc("/web/dataset/call_kw", {
                    model: "shift.shift",
                    method: "register_ftop_shift",
                    args: [parseInt(self.shift_id, 10)],
                    kwargs: {},
                });
                if (registration_id) {
                    $(`#btn-add-${self.shift_id}`)
                        .removeAttr("data-bs-toggle")
                        .removeAttr("data-bs-target")
                        .css({color: "grey"});
                    const $seats = $(`#avalable-seats-${self.shift_id}`);
                    $seats.text(parseInt($seats.text(), 10) - 1);
                    self._hideProgrammerModal();
                } else if (msg) {
                    self._showErrorModal("", msg);
                }
            } catch (error) {
                const body =
                    (error.data && error.data.arguments && error.data.arguments[0]) ||
                    "";
                self._showErrorModal(error.message, body);
            } finally {
                $(btn_check).removeAttr("disabled");
            }
        });
    },
});
