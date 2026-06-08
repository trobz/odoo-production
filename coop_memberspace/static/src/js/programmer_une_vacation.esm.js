import {copyToClipboard} from "./style.esm";
import publicWidget from "@web/legacy/js/public/public_widget";
import {rpc} from "@web/core/network/rpc";

export default publicWidget.registry.programmer_une_vacation =
    publicWidget.Widget.extend({
        selector: ".programmer_une_vacation",

        _getLangContext() {
            const lang = document.documentElement.lang?.replace(/-/g, "_");
            return lang ? {lang} : {};
        },

        parse_body_ftop_programmer(shift) {
            return `
        <tr style="${shift.css_style || ""}">
            <td id="week-${shift.id}">${shift.week_name || ""}</td>
            <td scope="row"><span id="time-${shift.id}">${shift.date_begin[0] + " "}</span></td>
            <td id="hour-${shift.id}">${shift.date_begin[1]}</td>
            <td id="avalable-seats-${shift.id}"><span>${shift.seats_avail}</span></td>
            <td>
                <a><span class="fa fa-user-plus"
                    id="btn-add-${shift.id}" shift-id="${shift.id}"></span></a>
            </td>
        </tr>`;
        },

        post_create_shift() {
            return true;
        },

        start() {
            const self = this;

            $(".toggle-ftop-programmer").on("click", async function () {
                const button_modal = this;
                $(button_modal).prop("disabled", true);
                $(".ftop-programmer-text").addClass("hide");
                $(".toggle-ftop-spinner-icon").removeClass("hide");
                $(".toggle-ftop-spinner-text").removeClass("hide");
                $(".body_ftop_programmer").empty();

                try {
                    const shifts = await rpc("/web/dataset/call_kw", {
                        model: "res.users",
                        method: "ftop_get_shift",
                        args: [],
                        kwargs: {},
                    });
                    shifts.forEach(function (shift) {
                        $(".body_ftop_programmer").append(
                            self.parse_body_ftop_programmer(shift)
                        );
                        $(`#btn-add-${shift.id}`).on("click", function () {
                            self.shift_id = $(this).attr("shift-id");
                            $(`#modal_time`).text($(`#time-${self.shift_id}`).text());
                            $(`#modal_hour`).text($(`#hour-${self.shift_id}`).text());
                            const BS = window.Modal || window.bootstrap?.Modal;
                            if (BS) {
                                BS.getOrCreateInstance(
                                    document.getElementById("programmer_modal")
                                ).show();
                            }
                        });
                    });
                    new (window.Modal || window.bootstrap?.Modal)(
                        document.getElementById("ftop_programmer_modal")
                    ).show();
                } finally {
                    $(".ftop-programmer-text").removeClass("hide");
                    $(".toggle-ftop-spinner-icon").addClass("hide");
                    $(".toggle-ftop-spinner-text").addClass("hide");
                    $(button_modal).prop("disabled", false);
                }
            });

            // eslint-disable-next-line complexity
            $(".fa.fa-check").on("click", async function (e) {
                e.preventDefault();
                const btn_check = this;
                $(btn_check).attr("disabled", "disabled");
                try {
                    const [result, coordinators, msg] = await rpc(
                        "/web/dataset/call_kw",
                        {
                            model: "shift.shift",
                            method: "register_ftop_shift",
                            args: [parseInt(self.shift_id, 10)],
                            kwargs: {context: self._getLangContext()},
                        }
                    );
                    if (result) {
                        self.post_create_shift();
                        const time = $(`#time-${self.shift_id}`).html();
                        const hour = $(`#hour-${self.shift_id}`).html();
                        const new_shift = `
                        <tr>
                            <td scope="row">${time + " "}</td>
                            <td>${hour}</td>
                            <td>
                                <span>
                                    <span>${coordinators[0] + " "}</span>
                                    <i data-bs-toggle="tooltip"
                                       title="You can contact your coordinators by writing to ${coordinators[1] + " "} (cliquez pour copier l'adresse)"
                                       class="fa fa-question-circle js-copy"
                                       data-copy="${coordinators[1]}"></i>
                                </span>
                            </td>
                            <td>
                                <a><button type="button" style="border: 0px; background-color: transparent"
                                    class="fa fa-times cancel-ftop-shift"
                                    registration-id="${result}"
                                    registration-name="${time + " " + hour}"></button></a>
                            </td>
                        </tr>`;
                        const $newRow = $(new_shift);
                        $(".ftop-programmer-une-vacation-body").append($newRow);
                        // Init Bootstrap 5 tooltips on new row
                        $newRow.find('[data-bs-toggle="tooltip"]').each(function () {
                            const BS_Tooltip =
                                window.Tooltip || window.bootstrap?.Tooltip;
                            if (BS_Tooltip) {
                                BS_Tooltip.getOrCreateInstance(this);
                            }
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
                    } else if (msg) {
                        $("#error_body").text(msg);
                        (window.Modal || window.bootstrap?.Modal)
                            ?.getInstance(document.getElementById("programmer_modal"))
                            ?.hide();
                        new (window.Modal || window.bootstrap?.Modal)(
                            document.getElementById("error_modal")
                        ).show();
                    }
                } catch (error) {
                    $("#error_header").text(error.message || "");
                    $("#error_body").text((error.data && error.data.message) || "");
                    (window.Modal || window.bootstrap?.Modal)
                        ?.getInstance(document.getElementById("programmer_modal"))
                        ?.hide();
                    new (window.Modal || window.bootstrap?.Modal)(
                        document.getElementById("error_modal")
                    ).show();
                } finally {
                    $(btn_check).removeAttr("disabled");
                }
            });

            // Delegate .js-copy clicks for dynamically added rows
            $(document).on(
                "click",
                ".ftop-programmer-une-vacation-body .js-copy",
                function () {
                    copyToClipboard($(this).attr("data-copy"), this);
                }
            );
        },
    });
