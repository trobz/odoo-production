async function _execCopy(text) {
    if (navigator.clipboard) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch {
            // Fall through to legacy method
        }
    }
    const area = document.createElement("textarea");
    area.value = text;
    area.style.cssText = "position:fixed;opacity:0";
    document.body.appendChild(area);
    area.focus();
    area.select();
    const ok = document.execCommand("copy");
    document.body.removeChild(area);
    return ok;
}

function _showCopiedTooltip(triggerEl) {
    const BS_Tooltip = window.Tooltip || window.bootstrap?.Tooltip;
    if (!BS_Tooltip || !triggerEl) return;
    const instance = BS_Tooltip.getOrCreateInstance(triggerEl);
    const originalTitle =
        triggerEl.getAttribute("title") ||
        triggerEl.getAttribute("data-bs-original-title") ||
        "";
    triggerEl.setAttribute("data-bs-original-title", "Copied!");
    instance.show();
    setTimeout(() => {
        instance.hide();
        triggerEl.setAttribute("data-bs-original-title", originalTitle);
    }, 1500);
}

export async function copyToClipboard(text, triggerEl) {
    const ok = await _execCopy(text);
    _showCopiedTooltip(ok ? triggerEl : null);
}

$(function () {
    // Bootstrap 5 tooltips
    const BS_Tooltip = window.Tooltip || window.bootstrap?.Tooltip;
    if (BS_Tooltip) {
        document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
            BS_Tooltip.getOrCreateInstance(el);
        });
    }

    // Copy-to-clipboard buttons already in DOM at load time
    $(document).on("click", ".js-copy", function () {
        copyToClipboard($(this).attr("data-copy"), this);
    });
});
