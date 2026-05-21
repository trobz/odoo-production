import {_t} from "@web/core/l10n/translation";
import publicWidget from "@web/legacy/js/public/public_widget";
import {rpc} from "@web/core/network/rpc";
import {showErrorMsg} from "./style.esm";

export default publicWidget.registry.mywork_ftop = publicWidget.Widget.extend({
    selector: ".mywork_ftop",
    start() {
        const self = this;
        $(".mywork_ftop").on("click", ".cancel-ftop-shift", async function () {
            const registration_id = parseInt($(this).attr("registration-id"), 10);
            const registration_name = $(this).attr("registration-name");
            const res = await rpc("/web/dataset/call_kw", {
                model: "shift.registration",
                method: "check_cancel_ftop_shift",
                args: [[registration_id]],
                kwargs: {},
            });
            if (res.code === 0) {
                showErrorMsg(res.msg);
            } else {
                self._showCancelConfirmModal(res, registration_name, registration_id);
            }
        });
    },

    _showCancelConfirmModal(res, registration_name, registration_id) {
        const self = this;
        // Remove any previous dynamic modal
        document.getElementById("ftop_cancel_confirm_modal_dyn")?.remove();
        const wrapper = document.createElement("div");
        wrapper.innerHTML = `
            <div class="modal fade" id="ftop_cancel_confirm_modal_dyn" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${_t("Confirmation")}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            ${res.data.msg} <strong>${registration_name}</strong>. ${res.data.confirm_msg}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">${_t("Cancel")}</button>
                            <button type="button" class="btn btn-primary js-ftop-confirm">${res.data.confirm_btn_label}</button>
                        </div>
                    </div>
                </div>
            </div>`;
        document.body.appendChild(wrapper.firstElementChild);
        const modalEl = document.getElementById("ftop_cancel_confirm_modal_dyn");
        const BS_Modal = window.Modal || window.bootstrap?.Modal;
        const modal = new BS_Modal(modalEl);
        modalEl
            .querySelector(".js-ftop-confirm")
            .addEventListener("click", function () {
                modal.hide();
                self.do_cancel_ftop_registration(registration_id);
            });
        modalEl.addEventListener("hidden.bs.modal", function () {
            modalEl.remove();
        });
        modal.show();
    },

    async do_cancel_ftop_registration(registration_id) {
        await rpc("/web/dataset/call_kw", {
            model: "shift.registration",
            method: "do_cancel_ftop_shift",
            args: [[registration_id]],
            kwargs: {},
        });
        window.location.reload();
    },
});
