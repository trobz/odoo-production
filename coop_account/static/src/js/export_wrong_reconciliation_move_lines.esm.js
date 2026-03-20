import {AlertDialog} from "@web/core/confirmation_dialog/confirmation_dialog";
import {_t} from "@web/core/l10n/translation";
import {download} from "@web/core/network/download";
import {registry} from "@web/core/registry";
import {rpc} from "@web/core/network/rpc";

export function exportWrongReconciliationMoveLines(env) {
    try {
        rpc("/coop_account/export_wrong_reconciliation_ml", {}).then(async (data) => {
            return await download({
                data: {
                    data: data,
                },
                url: `/web/export/xlsx`,
            });
        });
    } catch {
        env.services.dialog.add(AlertDialog, {
            title: _t("Error"),
            message: _t("An error occurred while exporting the move lines."),
        });
    }
}

registry
    .category("actions")
    .add("export_wrong_reconciliation_move_lines", exportWrongReconciliationMoveLines);
