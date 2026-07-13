import {CalendarCommonRenderer} from "@web/views/calendar/calendar_common/calendar_common_renderer";
import {patch} from "@web/core/utils/patch";

patch(CalendarCommonRenderer.prototype, {
    eventClassNames({event}) {
        const classesToAdd = super.eventClassNames(...arguments);
        const record = this.props.model.records[event.id];
        if (record && record.rawRecord.from_task) {
            classesToAdd.push("o_event_from_task");
        }
        return classesToAdd;
    },
});
