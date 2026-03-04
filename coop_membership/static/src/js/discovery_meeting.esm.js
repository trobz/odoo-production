/* global grecaptcha */

const DOB_DISPLAY_FORMAT = "dd/MM/yyyy";
const DOB_STORAGE_FORMAT = "yyyy-MM-dd";

function parseDob(value) {
    if (!value) {
        return null;
    }
    const displayDate = luxon.DateTime.fromFormat(value, DOB_DISPLAY_FORMAT, {
        locale: "fr",
    });
    if (displayDate.isValid) {
        return displayDate;
    }
    const isoDate = luxon.DateTime.fromFormat(value, DOB_STORAGE_FORMAT, {
        locale: "fr",
    });
    return isoDate.isValid ? isoDate : null;
}

function showValidate(input) {
    const wrapper = input.parentElement;
    wrapper?.classList.add("alert-validate");
}

function hideValidate(input) {
    const wrapper = input.parentElement;
    wrapper?.classList.remove("alert-validate");
    for (const button of wrapper?.querySelectorAll(".btn-hide-validate") || []) {
        button.remove();
    }
}

function validate(inputField) {
    const fieldType = inputField.getAttribute("type") || "";
    const fieldName = inputField.getAttribute("name") || "";
    const value = inputField.value.trim();

    if (fieldType === "email" || fieldName === "email") {
        return (
            value.match(
                /^([a-zA-Z0-9_.-]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9-]+\.)+))([a-zA-Z]{1,5}|[0-9]{1,3})(\]?)$/
            ) !== null
        );
    }

    if (fieldName === "dob") {
        const dob = parseDob(value);
        if (!dob) {
            return false;
        }
        return luxon.DateTime.now().year - dob.year >= 18;
    }

    return value !== "";
}

function validateRecaptcha() {
    return typeof grecaptcha !== "undefined" && grecaptcha.getResponse().length > 0;
}

function initDobInput() {
    const dobInput = document.querySelector("#dob_datepicker");
    if (!dobInput) {
        return;
    }

    const initialDob = parseDob(dobInput.value.trim());
    dobInput.type = "date";
    dobInput.min = "1900-01-01";
    dobInput.max = luxon.DateTime.now().toFormat(DOB_STORAGE_FORMAT);
    if (initialDob) {
        dobInput.value = initialDob.toFormat(DOB_STORAGE_FORMAT);
    }
}

function normalizeDobValueForSubmit() {
    const dobInput = document.querySelector("#dob_datepicker");
    if (!dobInput) {
        return;
    }

    const parsedDate = parseDob(dobInput.value.trim());
    if (!parsedDate) {
        return;
    }
    dobInput.value = parsedDate.toFormat(DOB_STORAGE_FORMAT);
}

function initDiscoveryMeetingForm() {
    initDobInput();

    const optionErrors = document.querySelectorAll(".validate-option-event");
    for (const node of optionErrors) {
        node.style.display = "none";
    }

    const inputs = Array.from(document.querySelectorAll(".validate-input .input100"));
    for (const input of inputs) {
        input.addEventListener("blur", () => {
            if (!validate(input)) {
                showValidate(input);
            }
        });
    }

    const formInputs = document.querySelectorAll(".validate-form .input100");
    for (const input of formInputs) {
        input.addEventListener("focus", () => hideValidate(input));
    }

    const forms = document.querySelectorAll(".validate-form");
    for (const form of forms) {
        form.addEventListener("submit", (event) => {
            normalizeDobValueForSubmit();
            let check = true;
            const radioChecked = document.querySelectorAll(
                ".validate-input-option:checked"
            ).length;

            for (const input of inputs) {
                if (!validate(input)) {
                    showValidate(input);
                    check = false;
                } else if (radioChecked === 0) {
                    for (const node of optionErrors) {
                        node.style.display = "block";
                    }
                    check = false;
                }
            }

            check = check && validateRecaptcha();
            if (!check) {
                event.preventDefault();
            }
        });
    }
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initDiscoveryMeetingForm);
} else {
    initDiscoveryMeetingForm();
}
