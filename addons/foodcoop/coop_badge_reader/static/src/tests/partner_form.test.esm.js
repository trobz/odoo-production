import {describe, expect, test} from "@odoo/hoot";
import {makeMockEnv, onRpc} from "@web/../tests/web_test_helpers";
import {PartnerFormComponent} from "@coop_badge_reader/components/partner_form/partner_form.esm";
import {mockPartnerData} from "./helpers.esm";

describe.current.tags("headless");

describe("PartnerFormComponent", () => {
    test("renders with correct props", async () => {
        const props = {
            displayBackButton: true,
            onClickBack: () => {
                return;
            },
            selectedPartnerId: 1,
        };

        onRpc("res.partner", "action_grace_partner", () => {
            return false;
        });

        onRpc("res.partner", "searchRead", () => {
            return [mockPartnerData];
        });

        await makeMockEnv();
        const component = new PartnerFormComponent();
        component.props = props;
        await component.setup();

        expect(component.props.displayBackButton).toBe(true);
        expect(component.props.selectedPartnerId).toBe(1);
    });

    test("getCooperativeStateClass returns correct class for up_to_date", () => {
        const component = new PartnerFormComponent();
        const result = component.getCooperativeStateClass("up_to_date");
        expect(result).toBe("label-success");
    });

    test("getCooperativeStateClass returns correct class for alert", () => {
        const component = new PartnerFormComponent();
        const result = component.getCooperativeStateClass("alert");
        expect(result).toBe("label-warning");
    });

    test("getCooperativeStateClass returns correct class for delay", () => {
        const component = new PartnerFormComponent();
        const result = component.getCooperativeStateClass("delay");
        expect(result).toBe("label-warning");
    });

    test("getCooperativeStateClass returns correct class for suspended", () => {
        const component = new PartnerFormComponent();
        const result = component.getCooperativeStateClass("suspended");
        expect(result).toBe("label-danger");
    });

    test("getCooperativeStateClass returns correct class for blocked", () => {
        const component = new PartnerFormComponent();
        const result = component.getCooperativeStateClass("blocked");
        expect(result).toBe("label-danger");
    });

    test("getCooperativeStateClass returns default class for unknown state", () => {
        const component = new PartnerFormComponent();
        const result = component.getCooperativeStateClass("unknown_state");
        expect(result).toBe("label-default");
    });

    test("getCooperativeStateLabel returns correct label for up_to_date", () => {
        const component = new PartnerFormComponent();
        const result = component.getCooperativeStateLabel("up_to_date");
        expect(result).toBe("Up to date");
    });

    test("getCooperativeStateLabel returns correct label for alert", () => {
        const component = new PartnerFormComponent();
        const result = component.getCooperativeStateLabel("alert");
        expect(result).toBe("Alert");
    });

    test("getCooperativeStateLabel returns correct label for delay", () => {
        const component = new PartnerFormComponent();
        const result = component.getCooperativeStateLabel("delay");
        expect(result).toBe("Grace period granted");
    });

    test("getCooperativeStateLabel returns correct label for suspended", () => {
        const component = new PartnerFormComponent();
        const result = component.getCooperativeStateLabel("suspended");
        expect(result).toBe("Suspended");
    });

    test("getCooperativeStateLabel returns raw state for unknown state", () => {
        const component = new PartnerFormComponent();
        const result = component.getCooperativeStateLabel("unknown_state");
        expect(result).toBe("unknown_state");
    });
});
