import {KanbanProjectRenderer} from "./kanban_project_renderer.esm";
import {projectTaskKanbanView} from "@project/views/project_task_kanban/project_task_kanban_view";
import {registry} from "@web/core/registry";

const projectLegendKanbanView = {
    ...projectTaskKanbanView,
    Renderer: KanbanProjectRenderer,
};

registry.category("views").add("project_legend_kanban", projectLegendKanbanView);
