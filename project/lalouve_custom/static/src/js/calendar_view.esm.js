import { patch } from "@web/core/utils/patch";
import { AttendeeCalendarController } from "@calendar/views/attendee_calendar/attendee_calendar_controller";
import { CalendarController } from "@web/views/calendar/calendar_controller";

/**
 * In Odoo 12, quick_add=false made clicking on a date open a full form dialog.
 * In Odoo 18, AttendeeCalendarController.editRecord ignores new records (no id),
 * so nothing happens. We patch it to fall back to the base class behavior
 * (open FormViewDialog) when event_open_popup=true and creating a new record.
 */
patch(AttendeeCalendarController.prototype, {
    async editRecord(record, context = {}) {
        if (!record.id && this.model.hasEditDialog) {
            // New record + event_open_popup=true → open full form as dialog
            return CalendarController.prototype.editRecord.call(this, record, context, false);
        }
        return super.editRecord(...arguments);
    },
});
