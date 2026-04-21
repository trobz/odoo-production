import {FormController} from "@web/views/form/form_controller";
import {ListController} from "@web/views/list/list_controller";
import {patch} from "@web/core/utils/patch";
import {session} from "@web/session";

export async function getResultAccessButtons(component) {
    const ctx = component.props?.context || {};
    const uid = ctx.uid || session.uid;
    const resModel = component.props?.resModel;
    if (!resModel || !uid) {
        return;
    }
    return component.orm.call("res.users", "check_access_buttons", [uid, resModel], {
        context: ctx,
    });
}

patch(FormController.prototype, {
    async setup() {
        super.setup();
        this.resultAccessButtons = await getResultAccessButtons(this);
    },
    get actionMenuItems() {
        const {actionMenus} = this.props.info;
        const res = super.actionMenuItems;
        if (
            this.forceHideActionMenuItems &&
            this.resultAccessButtons === "saisie_group_partner"
        ) {
            res.print = actionMenus?.print;
            return res;
        }
        return res;
    },
});
patch(ListController.prototype, {
    async setup() {
        super.setup();
        this.resultAccessButtons = await getResultAccessButtons(this);
    },
    get actionMenuItems() {
        const {actionMenus} = this.props.info;
        const res = super.actionMenuItems;
        if (
            this.forceHideActionMenuItems &&
            this.resultAccessButtons === "saisie_group_partner"
        ) {
            res.print = actionMenus?.print;
            return res;
        }
        return super.actionMenuItems;
    },
});
