import {describe, expect, test} from "@odoo/hoot";
import {badgeReaderApp} from "@coop_badge_reader/app/badge_reader_app";
import {makeMockEnv} from "@web/../tests/web_test_helpers";

describe.current.tags("headless");

describe("badgeReaderApp", () => {
    test("app has correct default state", async () => {
        await makeMockEnv();

        const app = new badgeReaderApp({
            companyId: 1,
            companyName: "Test Company",
        });

        expect(app.state.active_display).toBe("main");
        expect(app.state.previous_display).toBe("main");
        expect(app.partners.partnerIds).toEqual([]);
        expect(app.partners.selectedPartnerId).toBe(null);
    });

    test("displayBackButton returns false when active_display is main", () => {
        const app = new badgeReaderApp({
            companyId: 1,
            companyName: "Test Company",
        });

        expect(app.displayBackButton).toBe(false);
    });

    test("displayBackButton returns true when active_display is not main", () => {
        const app = new badgeReaderApp({
            companyId: 1,
            companyName: "Test Company",
        });
        app.state.active_display = "partner_form";

        expect(app.displayBackButton).toBe(true);
    });

    test("switchDisplay allows valid display transitions", () => {
        const app = new badgeReaderApp({
            companyId: 1,
            companyName: "Test Company",
        });

        app.switchDisplay("partner_form");
        expect(app.state.active_display).toBe("partner_form");
        expect(app.state.previous_display).toBe("main");
    });

    test("switchDisplay rejects invalid display transitions", () => {
        const app = new badgeReaderApp({
            companyId: 1,
            companyName: "Test Company",
        });

        app.switchDisplay("invalid_screen");
        expect(app.state.active_display).toBe("main");
    });

    test("switchDisplay resets when going back from partner_list to partner_form", () => {
        const app = new badgeReaderApp({
            companyId: 1,
            companyName: "Test Company",
        });

        app.state.active_display = "partner_list";
        app.state.previous_display = "partner_form";
        app.switchDisplay("partner_form");

        expect(app.state.active_display).toBe("main");
        expect(app.state.previous_display).toBe("main");
    });

    test("setPartnerSelected sets selected partner ID", () => {
        const app = new badgeReaderApp({
            companyId: 1,
            companyName: "Test Company",
        });

        app.setPartnerSelected(42);
        expect(app.partners.selectedPartnerId).toBe(42);
    });

    test("setPartnerIds sets multiple partner IDs", () => {
        const app = new badgeReaderApp({
            companyId: 1,
            companyName: "Test Company",
        });

        app.setPartnerIds([1, 2, 3]);
        expect(app.partners.partnerIds).toEqual([1, 2, 3]);
    });

    test("resetSearch clears all search values", () => {
        const app = new badgeReaderApp({
            companyId: 1,
            companyName: "Test Company",
        });

        app.searchValue.barcode = "test_barcode";
        app.searchValue.barcode_base = "test_base";
        app.searchValue.partner_name = "test_name";
        app.errorMessage.message = "error";

        app.resetSearch();

        expect(app.searchValue.barcode).toBe("");
        expect(app.searchValue.barcode_base).toBe("");
        expect(app.searchValue.partner_name).toBe("");
        expect(app.errorMessage.message).toBe("");
    });

    test("clearResults clears partner selections", () => {
        const app = new badgeReaderApp({
            companyId: 1,
            companyName: "Test Company",
        });

        app.setPartnerIds([1, 2, 3]);
        app.setPartnerSelected(1);

        app.clearResults();

        expect(app.partners.partnerIds).toEqual([]);
        expect(app.partners.selectedPartnerId).toBe(null);
    });

    test("onInputSearch updates search value", () => {
        const app = new badgeReaderApp({
            companyId: 1,
            companyName: "Test Company",
        });

        app.onInputSearch("barcode", {target: {value: "test_barcode"}});

        expect(app.searchValue.barcode).toBe("test_barcode");
    });

    test("attributesFieldsSearch returns correct field definitions", () => {
        const app = new badgeReaderApp({
            companyId: 1,
            companyName: "Test Company",
        });

        const fields = app.attributesFieldsSearch;

        expect(fields.barcode.label).toBe("Barcode");
        expect(fields.barcode.placeholder).toBe("Scan or enter barcode");
        expect(fields.barcode_base.label).toBe("Member number");
        expect(fields.partner_name.label).toBe("Name");
    });

    test("onSelectPartner switches to partner_form", () => {
        const app = new badgeReaderApp({
            companyId: 1,
            companyName: "Test Company",
        });

        app.onSelectPartner(42);

        expect(app.state.previous_display).toBe("partner_list");
        expect(app.state.active_display).toBe("partner_form");
        expect(app.partners.selectedPartnerId).toBe(42);
    });

    test("onClickBack returns to previous display", () => {
        const app = new badgeReaderApp({
            companyId: 1,
            companyName: "Test Company",
        });

        app.state.active_display = "partner_form";
        app.state.previous_display = "main";

        app.onClickBack();

        expect(app.state.active_display).toBe("main");
    });
});

describe("Search functionality", () => {
    test("onSearch shows error when no search value entered", async () => {
        const app = new badgeReaderApp({
            companyId: 1,
            companyName: "Test Company",
        });

        await app.onSearch();

        expect(app.errorMessage.message).toBe("Please enter a search value");
    });

    test("_renderSearchResults shows error when no partners found", () => {
        const app = new badgeReaderApp({
            companyId: 1,
            companyName: "Test Company",
        });

        app._renderSearchResults("barcode", []);

        expect(app.errorMessage.message).toBe("Barcode incorrect");
    });

    test("_renderSearchResults switches to partner_form when single partner found", () => {
        const app = new badgeReaderApp({
            companyId: 1,
            companyName: "Test Company",
        });

        app._renderSearchResults("barcode", [42]);

        expect(app.state.active_display).toBe("partner_form");
        expect(app.partners.selectedPartnerId).toBe(42);
    });

    test("_renderSearchResults switches to partner_list when multiple partners found", () => {
        const app = new badgeReaderApp({
            companyId: 1,
            companyName: "Test Company",
        });

        app._renderSearchResults("barcode", [1, 2, 3]);

        expect(app.state.active_display).toBe("partner_list");
        expect(app.partners.partnerIds).toEqual([1, 2, 3]);
    });

    test("_searchNotFound shows correct error for barcode", () => {
        const app = new badgeReaderApp({
            companyId: 1,
            companyName: "Test Company",
        });

        app._searchNotFound("barcode");

        expect(app.errorMessage.message).toBe("Barcode incorrect");
    });

    test("_searchNotFound shows correct error for barcode_base", () => {
        const app = new badgeReaderApp({
            companyId: 1,
            companyName: "Test Company",
        });

        app._searchNotFound("barcode_base");

        expect(app.errorMessage.message).toBe("Member number incorrect");
    });

    test("_searchNotFound shows correct error for partner_name", () => {
        const app = new badgeReaderApp({
            companyId: 1,
            companyName: "Test Company",
        });

        app._searchNotFound("partner_name");

        expect(app.errorMessage.message).toBe("No partner found with this name");
    });
});
