/* License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
import {Component, onMounted, useRef, useState} from "@odoo/owl";
import {Dialog} from "@web/core/dialog/dialog";
import {_t} from "@web/core/l10n/translation";

export class ManagerAuthPopup extends Component {
    static template = "pos_payment_credit_pin.ManagerAuthPopup";
    static components = {Dialog};
    static props = {
        title: String,
        loginPlaceholder: {type: String, optional: true},
        pinPlaceholder: {type: String, optional: true},
        confirmLabel: {type: String, optional: true},
        cancelLabel: {type: String, optional: true},
        getPayload: Function,
        close: Function,
    };
    static defaultProps = {
        loginPlaceholder: _t("Manager login"),
        pinPlaceholder: _t("Manager PIN"),
        confirmLabel: _t("Confirm"),
        cancelLabel: _t("Cancel"),
    };

    setup() {
        this.state = useState({
            login: "",
            pin: "",
        });
        this.loginRef = useRef("login");
        onMounted(() => {
            this.loginRef.el?.focus();
        });
    }

    confirm() {
        this.props.getPayload({
            login: this.state.login.trim(),
            pin: this.state.pin,
        });
        this.props.close();
    }

    close() {
        this.props.close();
    }

    onKeydown(ev) {
        if (
            ev.key !== undefined &&
            ev.key.toUpperCase() === "ENTER" &&
            this.canConfirm
        ) {
            ev.preventDefault();
            ev.stopPropagation();
            this.confirm();
        }
    }

    get canConfirm() {
        return this.state.login.trim() && this.state.pin;
    }
}
