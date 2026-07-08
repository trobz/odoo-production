import {ProjectTaskKanbanRenderer} from "@project/views/project_task_kanban/project_task_kanban_renderer";
import {onMounted, onWillUnmount} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";
import {renderToString} from "@web/core/utils/render";
import {useService} from "@web/core/utils/hooks";

// Patched directly on the shared base class instead of registered under a
// dedicated js_class: project_enterprise (when installed) also inherits
// project.view_task_kanban and sets its own js_class="project_enterprise_task_kanban"
// on the same node, which wins over ours depending on view-inheritance order
// and silently drops the legend. project_enterprise_task_kanban still reuses
// this same Renderer class (only its SearchModel differs), so patching here
// covers both community and enterprise kanban views.
patch(ProjectTaskKanbanRenderer.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        onMounted(() => this._renderProjectLegend());
        onWillUnmount(() => {
            if (this._onSearchModelUpdate) {
                this.env.searchModel.removeEventListener(
                    "update",
                    this._onSearchModelUpdate
                );
            }
        });
    },

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

        // Keep the legend in sync when the filter is removed some other way
        // than clicking a block, e.g. via the "x" on the search bar facet.
        this._onSearchModelUpdate = () => this._syncLegendSelection(panel);
        this.env.searchModel.addEventListener("update", this._onSearchModelUpdate);

        this._syncLegendSelection(panel);
    },

    // Selected tags are combined with OR: a task matches if it has any of
    // the currently selected tags (same semantics as Odoo's default "Tags"
    // search facet, where picking several values ORs them together).
    _filterByTag(tagId, tagName) {
        const searchModel = this.env.searchModel;

        // Find the currently active coop category filter, if any. Inactive
        // ones (e.g. removed via the search bar's "x") must be ignored:
        // toggling them again would reactivate them instead of leaving them
        // removed.
        const activeIds = new Set(
            searchModel.query.map((queryElem) => queryElem.searchItemId)
        );
        const existingFilter = Object.values(searchModel.searchItems).find(
            (item) =>
                item.type === "filter" &&
                item.isCoopCategFilter &&
                activeIds.has(item.id)
        );

        const selected = new Map(existingFilter ? existingFilter.coopCategTags : []);
        if (selected.has(tagId)) {
            selected.delete(tagId);
        } else {
            selected.set(tagId, tagName);
        }

        // Remove the existing combined filter before rebuilding it.
        if (existingFilter) {
            searchModel.toggleSearchItem(existingFilter.id);
        }

        if (selected.size) {
            searchModel.createNewFilters([
                {
                    description: [...selected.values()].join(", "),
                    domain: [["project_categ_id", "in", [...selected.keys()]]],
                    isCoopCategFilter: true,
                    coopCategTags: [...selected.entries()],
                },
            ]);
        }
    },

    _syncLegendSelection(panel) {
        const searchModel = this.env.searchModel;
        const activeIds = new Set(
            searchModel.query.map((queryElem) => queryElem.searchItemId)
        );
        const existingFilter = Object.values(searchModel.searchItems).find(
            (item) =>
                item.type === "filter" &&
                item.isCoopCategFilter &&
                activeIds.has(item.id)
        );
        const selectedIds = new Set(
            existingFilter ? existingFilter.coopCategTags.map(([id]) => id) : []
        );

        panel.querySelectorAll(".block-color-act").forEach((el) => {
            const tagId = parseInt(el.dataset.id, 10);
            el.classList.toggle("selected", selectedIds.has(tagId));
        });
    },
});
