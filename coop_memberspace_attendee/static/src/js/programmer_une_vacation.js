odoo.define("coop_memberspace_attendee.programmer_une_vacation", function (require) {
    "use strict";

    var sAnimations = require("website.content.snippets.animation");

    sAnimations.registry.programmer_une_vacation.include({
        start: function () {
            this._super.apply(this, arguments);
            const self = this;
            $(".programmer_une_vacation").on(
                "click",
                ".browse-expected-attendee",
                function (e) {
                    const shift_id = parseInt($(this).attr("shift-id"));
                    self._rpc({
                        model: "shift.shift",
                        method: "get_expected_attendee",
                        args: [[shift_id]],
                    }).then(function (partners) {
                        $(".modal_list_expected_attendee_body").empty();
                        if (partners.length) {
                            partners.forEach(function (partner, idx, array) {
                                const data = `
                                <tr>
                                    <td>${partner}</td>
                                </tr>
                            `;
                                $(".modal_list_expected_attendee_body").append(data);
                            });
                        }
                    });
                }
            );
        },
        parse_body_ftop_programmer: function (shift) {
            var body_ftop_programmer = `
            <tr style="${shift.css_style}">
                <td t-attf-id="week-${shift.id}">
                    ${shift.week_name || ""}
                </td>
                <td scope="row">
                    <span id="time-${shift.id}">${shift.date_begin[0] + " "}</span>
                </td>
                <td id="hour-${shift.id}">${shift.date_begin[1]}</td>
                <td>
                    <span>${shift.seats_reserved}</span>
                    ${this.get_reserved_seat_btn(shift)}

                </td>
                <td id="avalable-seats-${shift.id}"><span>${shift.seats_avail}</span></td>
                <td><a><span class="fa fa-user-plus" data-toggle="modal" data-target="#programmer_modal" id="btn-add-${shift.id}" shift-id="${shift.id}" /></a></td>
            </tr>`;
            return body_ftop_programmer;
        },
        get_reserved_seat_btn: function (shift) {
            if (shift.seats_reserved <= 0) {
                return "";
            }
            return `
                <span
                    data-toggle="modal" data-target="#modal_list_expected_attendee"
                    shift-id="${shift.id}"
                    class="fa fa-external-link browse-expected-attendee"/>
            `;
        },
    });
});
