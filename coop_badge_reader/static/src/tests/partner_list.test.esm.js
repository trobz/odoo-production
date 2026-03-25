import {describe, expect, test} from "@odoo/hoot";
import {PartnerListComponent} from "@coop_badge_reader/components/partner_list/partner_list";
import {mockPartnersData} from "./helpers.esm";
import {patchWithCleanup} from "@web/../tests/web_test_helpers";

describe.current.tags("headless");

describe("PartnerListComponent", () => {
    test("renders with correct props", () => {
        const props = {
            displayBackButton: true,
            partnerIds: [1, 2, 3],
            onSelectPartner: () => {
                return;
            },
            onClickBack: () => {
                return;
            },
        };

        const component = new PartnerListComponent();
        component.props = props;

        expect(component.props.displayBackButton).toBe(true);
        expect(component.props.partnerIds).toEqual([1, 2, 3]);
    });

    test("getCooperativeStateClass returns correct class for up_to_date", () => {
        const component = new PartnerListComponent();
        const result = component.getCooperativeStateClass("up_to_date");
        expect(result).toBe("label-success");
    });

    test("getCooperativeStateClass returns correct class for alert", () => {
        const component = new PartnerListComponent();
        const result = component.getCooperativeStateClass("alert");
        expect(result).toBe("label-warning");
    });

    test("getCooperativeStateClass returns correct class for delay", () => {
        const component = new PartnerListComponent();
        const result = component.getCooperativeStateClass("delay");
        expect(result).toBe("label-warning");
    });

    test("getCooperativeStateClass returns correct class for suspended", () => {
        const component = new PartnerListComponent();
        const result = component.getCooperativeStateClass("suspended");
        expect(result).toBe("label-danger");
    });

    test("getCooperativeStateClass returns correct class for not_concerned", () => {
        const component = new PartnerListComponent();
        const result = component.getCooperativeStateClass("not_concerned");
        expect(result).toBe("label-danger");
    });

    test("getCooperativeStateClass returns correct class for exempted", () => {
        const component = new PartnerListComponent();
        const result = component.getCooperativeStateClass("exempted");
        expect(result).toBe("label-success");
    });

    test("getCooperativeStateClass returns correct class for vacation", () => {
        const component = new PartnerListComponent();
        const result = component.getCooperativeStateClass("vacation");
        expect(result).toBe("label-danger");
    });

    test("getCooperativeStateClass returns default class for unknown state", () => {
        const component = new PartnerListComponent();
        const result = component.getCooperativeStateClass("unknown");
        expect(result).toBe("label-default");
    });

    test("getCooperativeStateLabel returns correct label for up_to_date", () => {
        const component = new PartnerListComponent();
        const result = component.getCooperativeStateLabel("up_to_date");
        expect(result).toBe("Up to date");
    });

    test("getCooperativeStateLabel returns correct label for alert", () => {
        const component = new PartnerListComponent();
        const result = component.getCooperativeStateLabel("alert");
        expect(result).toBe("Alert");
    });

    test("getCooperativeStateLabel returns correct label for delay", () => {
        const component = new PartnerListComponent();
        const result = component.getCooperativeStateLabel("delay");
        expect(result).toBe("Grace period granted");
    });

    test("getCooperativeStateLabel returns correct label for suspended", () => {
        const component = new PartnerListComponent();
        const result = component.getCooperativeStateLabel("suspended");
        expect(result).toBe("Suspended");
    });

    test("getCooperativeStateLabel returns correct label for exempted", () => {
        const component = new PartnerListComponent();
        const result = component.getCooperativeStateLabel("exempted");
        expect(result).toBe("Exempted");
    });

    test("getCooperativeStateLabel returns correct label for vacation", () => {
        const component = new PartnerListComponent();
        const result = component.getCooperativeStateLabel("vacation");
        expect(result).toBe("On leave");
    });

    test("getCooperativeStateLabel returns raw state for unknown state", () => {
        const component = new PartnerListComponent();
        const result = component.getCooperativeStateLabel("unknown");
        expect(result).toBe("unknown");
    });

    test("loadPartners returns empty array when partnerIds is empty", async () => {
        const component = new PartnerListComponent();
        component.props = {
            partnerIds: [],
        };

        const ormMock = {
            searchRead: () => Promise.resolve([]),
        };

        patchWithCleanup(component, {
            orm: ormMock,
        });

        const partners = await component.loadPartners();
        expect(partners).toEqual([]);
    });

    test("loadPartners returns partners with image_url", async () => {
        const component = new PartnerListComponent();
        component.props = {
            partnerIds: [1, 2],
        };

        const ormMock = {
            searchRead: () => Promise.resolve(mockPartnersData),
        };

        patchWithCleanup(component, {
            orm: ormMock,
        });

        const partners = await component.loadPartners();
        expect(partners.length).toBe(3);
        expect(partners[0].image_url).toBe(
            "/web/image?model=res.partner&id=1&field=image_1920"
        );
    });
});
