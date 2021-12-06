odoo.define('lalouve_custom.CalendarRenderer', function (require) {
    "use strict";

    var CalendarRenderer = require('web.CalendarRenderer');
    var core = require('web.core');
    var _t = core._t;
    var qweb = core.qweb;
    var config = require('web.config');
    var session = require('web.session');

    CalendarRenderer.include({
        _render: function () {
            var self = this;
            var selector = 'th.fc-axis';
            var checkSelector = 'div.llc-week-number';
            if (self.state.scale == 'month'){
                selector = 'td.fc-week-number';
            }
            return this._super.apply(this, arguments).then(function () {

                var tdWnEles = self.$('.o_calendar_view').find(selector);
                var checkEles = self.$('.o_calendar_view').find(checkSelector);
                var dates = [];
                if (tdWnEles && checkEles.length === 0)
                {
                    _.each(tdWnEles, function(ele){
                        if (ele.innerText && ele.nextElementSibling.dataset.date){
                            dates.push(ele.nextElementSibling.dataset.date);
                        }
                    });
                }
                if (dates.length > 0){
                    self._rpc({
                        model: 'calendar.event',
                        method: 'compute_week_name',
                        args: [dates],
                    }).then(function(result){
                        if (self.state.scale == 'month'){
                            self._addWeekNames_Month(tdWnEles,  result);
                        }
                        else {
                            self._addWeekNames_DayWeek(tdWnEles,  result);
                        }
                    });
                }
            });
        },
        _eventRender: function (event) {
            var qweb_context = {
                event: event,
                fields: this.state.fields,
                format: this._format.bind(this),
                isMobile: config.device.isMobile,
                read_only_mode: this.read_only_mode,
                record: event.record,
                user_context: session.user_context,
                widget: this,
            };
            this.qweb_context = qweb_context;
            if (_.isEmpty(qweb_context.record)) {
                return '';
            } else {
                return (this.qweb || qweb).render("calendar-box", qweb_context);
            }
        },
        _addWeekNames_Month: function(tdWnEles, res){
            var th = self.$('.o_calendar_view').find('th.fc-week-number');
            th.css('width', '58px');
            //Wrap by div tag to make the outerWidth();
            var thNewVal = '<div class="week-name-lb">' + th.html() + '</div>';
            th.html(thNewVal);
            _.each(tdWnEles, function(ele){
                let tdWNVal = '';
                if (ele.innerText && ele.nextElementSibling.dataset.date){
                    let _d = ele.nextElementSibling.dataset.date;
                    if (_d in res){
                        tdWNVal = res[_d];
                    }
                }
                let tdWn = '<div class="week-nb">' +
                        $(ele).html() +
                        '</div>' +
                        '<div class="llc-week-number week-name-' + tdWNVal + '">' +
                            '<div>'+ tdWNVal + '</div>' +
                    '</div>';
                $(ele).css('width', '58px');
                $(ele).html(tdWn);
            });
            //this.$calendar.fullCalendar('updateSize');
            // Trigger resize function to let the selection highlight works properly
            $(window).trigger('resize');
        },
        _addWeekNames_DayWeek: function(tdWnEles, res){
            _.each(tdWnEles, function(ele){
                let tdWNVal = '';
                if (ele.innerText && ele.nextElementSibling.dataset.date){
                    let _d = ele.nextElementSibling.dataset.date;
                    if (_d in res){
                        tdWNVal = res[_d];
                    }
                }
                $(ele).addClass('week-name-' + tdWNVal);
                let tdWn = '' +
                    '<div class="llc-week-number">' +
                        tdWNVal + ' ' + $(ele).html() +
                    '</div>';
                $(ele).html(tdWn);
            });
        },
    });

});
