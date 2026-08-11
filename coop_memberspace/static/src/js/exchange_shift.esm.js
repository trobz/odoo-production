import publicWidget from "@web/legacy/js/public/public_widget";
import {rpc} from "@web/core/network/rpc";
import {showErrorMsg} from "./style.esm";

function bsModal(id) {
    const el = document.getElementById(id);
    if (!el) return null;
    // Odoo 18 loads Bootstrap components individually; Modal is a direct global
    const BS_Modal = window.Modal || window.bootstrap?.Modal;
    if (!BS_Modal) return null;
    return BS_Modal.getOrCreateInstance(el);
}

export default publicWidget.registry.exchange_shift = publicWidget.Widget.extend({
    selector: ".exchange-shift",
    start() {
        const self = this;

        $(".exchange-shift").on("click", ".remove-proposal", function () {
            self.btn_remove = this;
            self.registration_id = parseInt($(this).attr("registration-id"), 10);
        });

        $(".exchange-shift").on("click", ".go-to-market", function () {
            self.go_to_market(this);
        });

        $("#modal_confirm_cancel_proposal").on(
            "click",
            ".cancel-proposal",
            async function () {
                const lang = document.documentElement.lang?.replace(/-/g, "_");
                await rpc("/web/dataset/call_kw", {
                    model: "shift.registration",
                    method: "remove_shift_regis_from_market",
                    args: [[self.registration_id]],
                    kwargs: {
                        context: {
                            ...(lang ? {lang} : {}),
                        },
                    },
                });
                const parent = $(self.btn_remove).parent();
                parent.empty().append(self.get_swap_btn_html(self.registration_id));
                bsModal("modal_confirm_cancel_proposal")?.hide();
                self.post_cancel_proposal();
            }
        );

        $(".exchange-shift").on(
            "click",
            ".browse-expected-attendee",
            async function () {
                const shift_id = parseInt($(this).attr("shift-id"), 10);
                const partners = await rpc("/web/dataset/call_kw", {
                    model: "shift.shift",
                    method: "get_expected_attendee",
                    args: [[shift_id]],
                    kwargs: {},
                });
                $(".modal_list_expected_attendee_body").empty();
                partners.forEach((partner) => {
                    const td = document.createElement("td");
                    td.textContent = partner;
                    const tr = document.createElement("tr");
                    tr.appendChild(td);
                    $(".modal_list_expected_attendee_body").append(tr);
                });
            }
        );

        $(".exchange-shift").on("click", ".select-shift-proposal", async function () {
            self.shift_on_market = parseInt($(this).attr("registration-id"), 10);
            self.shift_available = parseInt($(this).attr("shift-id"), 10);
            const btn = this;
            $(btn).prop("disabled", true);
            try {
                const shifts = await rpc("/web/dataset/call_kw", {
                    model: "shift.registration",
                    method: "shifts_to_proposal",
                    args: [[self.shift_on_market]],
                    kwargs: {},
                });
                $(".modal_exchange_shift_body").empty();
                if (!shifts.length) {
                    $(".create-proposal").addClass("d-none");
                    $("#modal_exchange_shift .confirm-shift-proposal").addClass(
                        "d-none"
                    );
                    $(".modal_exchange_shift_body").append(
                        '<tr class="text-center"><td>No shift available</td></tr>'
                    );
                    bsModal("modal_exchange_shift")?.show();
                } else if (shifts.length === 1) {
                    self.des_registration_id = shifts[0].id;
                    await self.show_shift_proposal_confirmation(
                        self.shift_on_market,
                        self.shift_available,
                        shifts[0].id
                    );
                    bsModal("modal_confirm_exchange_shift")?.show();
                } else {
                    shifts.forEach((shift) => {
                        $(".modal_exchange_shift_body").append(`
                            <tr>
                                <td>${shift.date}</td>
                                <td>${shift.hour}</td>
                                <td><input name="registration_input" id="${shift.id}" type="radio" value="${shift.id}" /></td>
                            </tr>`);
                    });
                    $("#modal_exchange_shift .confirm-shift-proposal").removeClass(
                        "d-none"
                    );
                    bsModal("modal_exchange_shift")?.show();
                }
            } finally {
                $(btn).prop("disabled", false);
            }
        });

        $(".exchange-shift").on("click", ".confirm-shift-proposal", async function () {
            const des_registration_id = parseInt(
                $("input[name=registration_input]:checked").val(),
                10
            );
            await self.show_shift_proposal_confirmation(
                self.shift_on_market,
                self.shift_available,
                des_registration_id
            );
            bsModal("modal_exchange_shift")?.hide();
        });

        $("#modal_confirm_exchange_shift").on(
            "click",
            ".create-proposal",
            async function () {
                let des_registration_id = parseInt(
                    $("input[name=registration_input]:checked").val(),
                    10
                );
                if (!des_registration_id && self.des_registration_id !== undefined) {
                    des_registration_id = self.des_registration_id;
                }
                const btn = this;
                $(btn).prop("disabled", true);
                try {
                    const lang = document.documentElement.lang?.replace(/-/g, "_");
                    await rpc("/web/dataset/call_kw", {
                        model: "shift.registration",
                        method: "create_proposal",
                        args: [
                            self.shift_on_market,
                            des_registration_id,
                            self.shift_available,
                        ],
                        kwargs: {
                            context: {
                                ...(lang ? {lang} : {}),
                            },
                        },
                    });
                    bsModal("modal_confirm_exchange_shift")?.hide();
                    window.location.reload();
                } catch {
                    bsModal("modal_confirm_exchange_shift")?.hide();
                } finally {
                    $(btn).prop("disabled", false);
                }
            }
        );
    },

    async go_to_market(btn) {
        const registration_id = parseInt($(btn).attr("registration-id"), 10);
        const lang = document.documentElement.lang?.replace(/-/g, "_");
        const res = await rpc("/web/dataset/call_kw", {
            model: "shift.registration",
            method: "add_shift_regis_to_market",
            args: [[registration_id]],
            kwargs: {
                context: {
                    ...(lang ? {lang} : {}),
                },
            },
        });
        if (res.code === 0) {
            showErrorMsg(res.msg);
        } else {
            $(btn).parent().empty().append(`
                <span>${this.get_cancel_label()} </span>
                <button class="material-icons button-icon remove-proposal"
                    registration-id="${registration_id}"
                    data-bs-toggle="modal" data-bs-target="#modal_confirm_cancel_proposal">remove_circle_outline</button>
            `);
        }
    },

    get_swap_btn_html(registration_id) {
        return `
            <button class="material-icons button-icon go-to-market" style="margin-right: 10px;"
                registration-id="${registration_id}">swap_horiz</button>`;
    },

    post_cancel_proposal() {
        // Intended to be overridden in subclasses
    },

    get_cancel_label() {
        return "En cours";
    },

    async show_shift_proposal_confirmation(
        src_registration_id,
        src_shift,
        des_registration_id
    ) {
        const lang = document.documentElement.lang?.replace(/-/g, "_");
        const resp = await rpc("/web/dataset/call_kw", {
            model: "shift.registration",
            method: "shifts_to_confirm",
            args: [src_registration_id, des_registration_id, src_shift],
            kwargs: {
                context: {
                    ...(lang ? {lang} : {}),
                },
            },
        });
        const code = resp[0];
        const mesg = resp[1];
        $(".modal_confirm_shift_body").empty().append(`<span>${mesg} </span>`);
        if (!des_registration_id || code === 0) {
            $(".create-proposal").addClass("d-none");
        } else {
            $(".create-proposal").removeClass("d-none");
        }
    },
});
