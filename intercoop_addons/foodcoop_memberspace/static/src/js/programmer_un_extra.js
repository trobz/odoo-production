odoo.define('foodcoop_memberspace.programmer_un_extra', function (require) {
    "use strict";

    var snippet_animation = require('web_editor.snippets.animation');
    var session = require('web.session');
    var Model = require('web.Model');
    var ajax = require("web.ajax");

    snippet_animation.registry.programmer_un_extra =
		snippet_animation.Class.extend({
            selector: '.programmer_un_extra',
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

                $('.fa.fa-check').on('click', function() {
                    let btn_add = this;
                    new Model('shift.ticket').call(
                        'search', [[['shift_id', '=', parseInt(self.shift_id)], ['shift_type', '=', 'ftop']]],
                        {"context": {'member_space': true}}
                    )
                    .then(function(data) {
                        if (data.length > 0) {
                            let vals = {
                                'state': 'draft',
                                'partner_id': parseInt(self.session.partner_id),
                                'shift_id': parseInt(self.shift_id),
                                'shift_ticket_id': parseInt(data[0]),
                                'related_extension_id': false
                            }
                            new Model('shift.registration').call(
                                'create', [vals], {"context": {'member_space': true}}
                            )
                            .then(function(result) {
                                $('#btn-add-' + self.shift_id).removeAttr("data-toggle").removeAttr("data-target").css({'color': 'red'});
                                let no_available_seats = '#avalable-seats-' + self.shift_id;
                                $(no_available_seats).text(parseInt($(no_available_seats).text()) - 1);
                                $('#programmer_un_extra_modal').modal('hide');
                            })
                            .fail(function(error, event) {
                                $('#programmer_un_extra_error_header').text(error.message);
                                $('#programmer_un_extra_error_body').text(error.data.message);
                                $('#programmer_un_extra_modal').modal('hide');
                                $('#programmer_un_extra_error_modal').modal('show');
                            });
                        }
                    })
                });
            }
        })
});