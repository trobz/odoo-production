import {describe} from "@odoo/hoot";
import {patchWithCleanup} from "@web/../tests/web_test_helpers";
import {url} from "@web/core/utils/urls";

describe.current.tags("headless");

export const mockBadgeReaderEnv = async () => {
    patchWithCleanup(url, (route, params) => {
        return `${route}?${new URLSearchParams(params).toString()}`;
    });
};

export const mockPartnerData = {
    id: 1,
    name: "Test Partner",
    street: "123 Test Street",
    street2: "Apt 1",
    zip: "12345",
    city: "Test City",
    customer: true,
    country_id: [1, "Test Country"],
    phone: "+1234567890",
    mobile: "+0987654321",
    bootstrap_cooperative_state: "up_to_date",
    cooperative_state: "up_to_date",
    display_name: "Test Partner",
    badge_to_distribute: false,
    contact_us_message: "",
    error_message: "",
};

export const mockPartnersData = [
    {
        id: 1,
        name: "Partner One",
        street: "Street 1",
        city: "City 1",
        bootstrap_cooperative_state: "up_to_date",
        cooperative_state: "up_to_date",
    },
    {
        id: 2,
        name: "Partner Two",
        street: "Street 2",
        city: "City 2",
        bootstrap_cooperative_state: "alert",
        cooperative_state: "alert",
    },
    {
        id: 3,
        name: "Partner Three",
        street: "Street 3",
        city: "City 3",
        bootstrap_cooperative_state: "delay",
        cooperative_state: "delay",
    },
];
