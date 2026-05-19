import publicWidget from "@web/legacy/js/public/public_widget";
import {rpc} from "@web/core/network/rpc";
import {session} from "@web/session";

export default publicWidget.registry.my_profile = publicWidget.Widget.extend({
    selector: ".my_profile",
    start() {
        const self = this;

        // Edit Phone number
        $(".btn-edit-phone").on("click", function () {
            $("input[name=mobile]").removeAttr("disabled").removeClass("input-no-edit");
            $("input[name=phone]").removeAttr("disabled").removeClass("input-no-edit");
            self.prev_mobile = $("input[name=mobile]").val();
            self.prev_phone = $("input[name=phone]").val();
            $(this).addClass("hide");
            $(this)
                .parent()
                .append(
                    '<div class="row">' +
                        '<div class="col-xs-6 col-sm-6 col-md-6 pd-l-20 pd-r-20"><button type="button" class="btn btn-default btn-cancel-edit-phone">Annuler</button></div>' +
                        '<div class="col-xs-6 col-sm-6 col-md-6 pd-l-20 pd-r-20"><button class="btn btn-primary">Submit</button></div>' +
                        "</div>"
                );
            $(".btn-cancel-edit-phone").on("click", function () {
                $("input[name=mobile]")
                    .attr("disabled", true)
                    .addClass("input-no-edit")
                    .val(self.prev_mobile);
                $("input[name=phone]")
                    .attr("disabled", true)
                    .addClass("input-no-edit")
                    .val(self.prev_phone);
                $(".btn-edit-phone").removeClass("hide");
                $(this).parents().eq(1).remove();
            });
        });

        // Edit address
        $(".btn-edit-address").on("click", function () {
            $(".address-no-edit").addClass("hide");
            $(".address-edit").removeClass("hide");
            self.prev_street = $("input[name=street]").val();
            self.prev_zip = $("input[name=zip]").val();
            self.prev_city = $("input[name=city]").val();
            $(this).addClass("hide");
            $(this)
                .parent()
                .append(
                    `<div class="row">
                    <div class="col-xs-6 col-sm-6 col-md-6 pd-l-20 pd-r-20">
                        <button type="button" class="btn btn-default btn-cancel-edit-address">Annuler</button>
                    </div>
                    <div class="col-xs-6 col-sm-6 col-md-6 pd-l-20 pd-r-20">
                        <button class="btn btn-primary">Submit</button>
                    </div>
                </div>`
                );
            $(".btn-cancel-edit-address").on("click", function () {
                $("input[name=street]").val(self.prev_street);
                $("input[name=zip]").val(self.prev_zip);
                $("input[name=city]").val(self.prev_city);
                $(".address-no-edit").removeClass("hide");
                $(".address-edit").addClass("hide");
                $(".btn-edit-address").removeClass("hide");
                $(this).parents().eq(1).remove();
            });
        });

        // Toggle public avatar / mobile / email
        $("input[name=public_avatar]").change(function () {
            rpc("/web/dataset/call_kw", {
                model: "res.partner",
                method: "write",
                args: [[session.partner_id], {public_avatar: this.checked}],
                kwargs: {},
            });
        });

        $("input[name=public_mobile]").change(function () {
            rpc("/web/dataset/call_kw", {
                model: "res.partner",
                method: "write",
                args: [[session.partner_id], {public_mobile: this.checked}],
                kwargs: {},
            });
        });

        $("input[name=public_email]").change(function () {
            rpc("/web/dataset/call_kw", {
                model: "res.partner",
                method: "write",
                args: [[session.partner_id], {public_email: this.checked}],
                kwargs: {},
            });
        });
    },
});
