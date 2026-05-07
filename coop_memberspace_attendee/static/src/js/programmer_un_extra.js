odoo.define("coop_memberspace_attendee.programmer_un_extra", function (require) {
    "use strict";

    var sAnimations = require("website.content.snippets.animation");

    sAnimations.registry.programmer_un_extra.include({
        start: function () {
            this._super.apply(this, arguments);
            const self = this;
            $(".programmer_un_extra").on(
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
    });
});
