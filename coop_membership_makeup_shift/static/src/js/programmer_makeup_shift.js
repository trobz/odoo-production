odoo.define('coop_memberspace.programmer_makeup_shift', function (require) {
    "use strict";

    var sAnimations = require('website.content.snippets.animation');
    var ajax = require("web.ajax");

    sAnimations.registry.programmer_makeup_shift =
        sAnimations.Class.extend({
            selector: '.programmer_makeup_shift',
            start: function () {
                var self = this;
                ajax.jsonRpc("/web/session/get_session_info", "call").then(function (sessiondata) {
                    self.session = sessiondata;
                });
                $('.fa.fa-user-plus').on('click', function() {
                    let shift_id = $(this).attr('data-shift-id');
                    self.shift_id = shift_id;
                    let time = $('#time-' + shift_id).text();
                    let hour = $('#hour-' + shift_id).text();
                    $('#modal_time').text(time);
                    $('#modal_hour').text(hour);
                });

                $('.fa.fa-check').on('click', function(e) {
                    e.preventDefault();
                    let btn_check = this;
                    $(btn_check).attr("disabled", "disabled");
                    self._rpc({
                        model: 'shift.shift',
                        method: 'register_makeup_shift',
                        args: [[parseInt(self.shift_id)]],
                    })
                    .then(function(resp) {
                        var code = resp[0];
                        var msg = resp[1];
                        if (code == 1) {
                            $('#btn-add-' + self.shift_id).removeAttr("data-toggle").removeAttr("data-target").css({'color': 'grey'});
                            let no_available_seats = '#avalable-seats-' + self.shift_id;
                            $(no_available_seats).text(parseInt($(no_available_seats).text()) - 1);
                            $('#programmer_modal').modal('hide');
                            $(btn_check).removeAttr("disabled");
                        }
                        else {
                            $(btn_check).removeAttr("disabled");
                            if (msg !== "")
                            {
                                $('#error_body').text(msg);
                                $('#programmer_modal').modal('hide');
                                $('#error_modal').modal('show');
                            }
                        }
                    })
                    .fail(function(error, event) {
                        $('#error_header').text(error.message);
                        $('#error_body').text(error.data.arguments[0] || '');
                        $('#programmer_modal').modal('hide');
                        $('#error_modal').modal('show');
                        $(btn_check).removeAttr("disabled");
                    });
                });
            }
        })
});
