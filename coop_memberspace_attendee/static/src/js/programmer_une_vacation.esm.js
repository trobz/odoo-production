import publicWidget from "@web/legacy/js/public/public_widget";
import {rpc} from "@web/core/network/rpc";

publicWidget.registry.programmer_une_vacation.include({
    get_reserved_seat_btn(shift) {
        if (shift.seats_reserved <= 0) {
            return "";
        }
        return `<span
            data-bs-toggle="modal"
            data-bs-target="#modal_list_expected_attendee"
            shift-id="${shift.id}"
            class="fa fa-external-link browse-expected-attendee"></span>`;
    },

    parse_body_ftop_programmer(shift) {
        return `
        <tr style="${shift.css_style || ""}">
            <td id="week-${shift.id}">${shift.week_name || ""}</td>
            <td scope="row"><span id="time-${shift.id}">${shift.date_begin[0] + " "}</span></td>
            <td id="hour-${shift.id}">${shift.date_begin[1]}</td>
            <td>
                <span>${shift.seats_reserved}</span>
                ${this.get_reserved_seat_btn(shift)}
            </td>
            <td id="avalable-seats-${shift.id}"><span>${shift.seats_avail}</span></td>
            <td><a><span class="fa fa-user-plus"
                data-bs-toggle="modal" data-bs-target="#programmer_modal"
                id="btn-add-${shift.id}" shift-id="${shift.id}"></span></a></td>
        </tr>`;
    },

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
