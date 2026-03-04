import {FormController} from "@web/views/form/form_controller";
import {KanbanController} from "@web/views/kanban/kanban_controller";
import {ListController} from "@web/views/list/list_controller";
import {patch} from "@web/core/utils/patch";
import {session} from "@web/session";
import {useService} from "@web/core/utils/hooks";

async function getUiAccess(component, resModel, uid, context) {
    if (!resModel) {
        return null;
    }
    return component.orm.call("res.users", "check_access_ui", [uid, resModel], {
        context: context,
    });
}

// eslint-disable-next-line complexity
async function checkHideButtons(component) {
    // Check to show/hide "New" button
    component.orm = useService("orm");
    const ctx = component.props?.context || {};
    const uid = ctx.uid || session.uid;
    const resModel = component.props?.resModel;
    if (!resModel || !uid) {
        return;
    }
    const result = await getUiAccess(component, resModel, uid, ctx);
    if (!result) {
        return;
    }
    if (!result.can_Create_Edit) {
        // Kanban and List views:
        if (component.props?.showButtons === true) {
            component.props.showButtons = false;
        }

        // Form view:
        if (
            Object.prototype.hasOwnProperty.call(component, "canCreate") &&
            component?.canCreate === true
        ) {
            component.canCreate = false;
        }
        if (
            Object.prototype.hasOwnProperty.call(component, "canEdit") &&
            component?.canEdit === true
        ) {
            component.canEdit = false;
        }
    }
    component.forceHideActionMenuItems = !result.actionMenuItems;
    component.forceHideCogMenuImport = !result.cogMenuImport;
    component.forceHideMailChatterTop = !result.o_mail_Chatter_top;
}

async function checkHideCogMenuImport(component) {
    // Check to show/hide "Import" button in cog menu
    if (!component.forceHideCogMenuImport) return;
    const config = component?.env?.config;
    if (!config) return;
    // Set import to false to hide the import button in cog menu
    config.viewArch.setAttribute("import", "false");
}

patch(FormController.prototype, {
    async setup() {
        super.setup();
        await checkHideButtons(this);
        if (this.env?.chatter) {
            this.env.chatter.forceHideMailChatterTop = this.forceHideMailChatterTop;
        }
    },
    get actionMenuItems() {
        if (this.forceHideActionMenuItems) {
            return {action: [], print: []};
        }
        return super.actionMenuItems;
    },
});
patch(KanbanController.prototype, {
    async setup() {
        super.setup();
        await checkHideButtons(this);
        await checkHideCogMenuImport(this);
    },
});
patch(ListController.prototype, {
    async setup() {
        super.setup();
        await checkHideButtons(this);
        await checkHideCogMenuImport(this);
    },
    get actionMenuItems() {
        if (this.forceHideActionMenuItems) {
            return {action: [], print: []};
        }
        return super.actionMenuItems;
    },
});
