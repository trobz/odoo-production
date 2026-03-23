import {Component} from "@odoo/owl";
import {Dialog} from "@web/core/dialog/dialog";

export class VerifyPaymentDialog extends Component {
    static template = "coop_point_of_sale.VerifyPaymentDialog";
    static components = {Dialog};
    static props = {
        thanks_message: {type: String},
        amount: {type: String},
        date: {type: String},
        order_messages: {type: String},
        signature: {type: String},
        cancel_callback: {type: Function},
        confirm: {type: Function},
        close: {type: Function},
    };

    onCancel() {
        this.props.cancel_callback();
        this.props.close();
    }

    onConfirm() {
        this.props.confirm();
        this.props.close();
    }
}
