import {ProjectTaskKanbanRenderer} from "@project/views/project_task_kanban/project_task_kanban_renderer";
import {onMounted} from "@odoo/owl";
import {renderToString} from "@web/core/utils/render";
import {useService} from "@web/core/utils/hooks";

export class KanbanProjectRenderer extends ProjectTaskKanbanRenderer {
    setup() {
        super.setup();
        this.orm = useService("orm");
        onMounted(() => this._renderProjectLegend());
    }

    async _renderProjectLegend() {
        document
            .querySelectorAll(".o_kanban_project_panel_section")
            .forEach((el) => el.remove());

        const context = this.props.list?.context || {};
        if (!context.default_project_id) return;

        const categories = await this.orm.call(
            "project.project",
            "get_kanban_categories",
            [[context.default_project_id]]
        );

        const html = renderToString("coop_project.ProjectKanban.Category", {
            categories,
        });
        const container = document.createElement("div");
        container.innerHTML = html;
        const panel = container.firstElementChild;

        const rootEl = this.rootRef.el;
        if (rootEl && rootEl.parentNode) {
            rootEl.parentNode.insertBefore(panel, rootEl);
        }

        panel.addEventListener("click", (ev) => {
            const target = ev.target.closest(".block-color-act");
            if (!target) return;
            const tagId = parseInt(target.dataset.id, 10);
            const tagName = target.dataset.categName;
            this._filterByTag(tagId, tagName);
        });
    }

    _filterByTag(tagId, tagName) {
        const searchModel = this.env.searchModel;

        // Find any currently active coop category filter. Inactive ones (e.g.
        // removed via the search bar's "x") must be ignored: toggling them
        // again would reactivate them instead of leaving them removed.
        const activeIds = new Set(searchModel.query.map((queryElem) => queryElem.searchItemId));
        const existingFilters = Object.values(searchModel.searchItems).filter(
            (item) => item.type === "filter" && item.isCoopCategFilter && activeIds.has(item.id)
        );
        const sameFilter = existingFilters.find((item) => item.coopCategId === tagId);

        // Remove existing category filters
        existingFilters.forEach((filter) => searchModel.toggleSearchItem(filter.id));

        // If a different category was clicked, activate it
        if (!sameFilter) {
            searchModel.createNewFilters([
                {
                    description: tagName,
                    domain: [["tag_ids", "in", [tagId]]],
                    isCoopCategFilter: true,
                    coopCategId: tagId,
                },
            ]);
        }
    }
}
