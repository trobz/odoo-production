import { patch } from "@web/core/utils/patch";
import { AttendeeCalendarCommonRenderer } from "@calendar/views/attendee_calendar/common/attendee_calendar_common_renderer";
import { useService } from "@web/core/utils/hooks";

/**
 * Inject a dedicated "W" column before Sunday showing the shift cycle week name
 * (A, B, C...) computed server-side via calendar.event::compute_week_name.
 */
patch(AttendeeCalendarCommonRenderer.prototype, {
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
    },

    /**
     * FullCalendar callback: called after the view's DOM is fully rendered.
     */
    viewDidMount({ el, view }) {
        super.viewDidMount(...arguments);
        this._injectWeekColumn(el).catch((e) =>
            console.error("[lalouve] week column error:", e)
        );
    },

    async _injectWeekColumn(el) {
        if (el.querySelector(".llc-w-col")) {
            return; // already injected for this render
        }

        // Gather the first-day-of-week date for each visible week row.
        // .fc-daygrid-week-number sits inside the first-day cell on desktop,
        // or inside .o-fc-week on mobile (after makeWeekColumn runs).
        const weekNumberEls = el.querySelectorAll(".fc-daygrid-week-number");
        if (!weekNumberEls.length) return;

        const rowDates = [];
        const rowWeekNums = [];
        for (const wn of weekNumberEls) {
            let dateEl = wn.closest("[data-date]");
            if (!dateEl) {
                // Mobile: wn moved to .o-fc-week; next sibling is the day cell
                const weekCol = wn.closest(".o-fc-week");
                if (weekCol) dateEl = weekCol.nextElementSibling;
            }
            rowDates.push(dateEl?.dataset?.date ?? null);
            rowWeekNums.push(wn.textContent.trim());
        }

        const validDates = rowDates.filter(Boolean);
        if (!validDates.length) return;

        const weekNames = await this.orm.call(
            "calendar.event",
            "compute_week_name",
            [validDates]
        );

        // Select all Sunday cells (header th + body td) — both carry fc-day-sun.
        // Insert a W cell before each one, matching the pattern of makeWeekColumn.
        const sunCells = el.querySelectorAll(".fc-day-sun");
        let bodyRowIdx = 0;

        for (const cell of sunCells) {
            const isHeader = cell.classList.contains("fc-col-header-cell");
            const newCell = document.createElement(isHeader ? "th" : "td");
            newCell.classList.add("llc-w-col");

            if (isHeader) {
                newCell.classList.add("llc-w-col-header");
                newCell.innerHTML =
                    '<div class="fc-scrollgrid-sync-inner">' +
                    '<span class="fc-col-header-cell-cushion">W</span>' +
                    "</div>";
            } else {
                const idx = bodyRowIdx++;
                const date = rowDates[idx] ?? null;
                const letter = date ? (weekNames[date] ?? "") : "";
                const weekNum = rowWeekNums[idx] ?? "";
                newCell.classList.add("llc-w-col-cell");
                newCell.innerHTML =
                    `<div class="llc-w-inner">` +
                    `<span class="llc-w-num">${weekNum}</span>` +
                    `<div class="llc-w-badge week-name-${letter}">${letter}</div>` +
                    `</div>`;
            }

            cell.parentNode.insertBefore(newCell, cell);
        }
    },
});
