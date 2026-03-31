import {KanbanProjectRenderer} from "./kanban_project_renderer.esm";
import {kanbanView} from "@web/views/kanban/kanban_view";
import {registry} from "@web/core/registry";

const projectLegendKanbanView = {
    ...kanbanView,
    Renderer: KanbanProjectRenderer,
};

registry.category("views").add("project_legend_kanban", projectLegendKanbanView);
