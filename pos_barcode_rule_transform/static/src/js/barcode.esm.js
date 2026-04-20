/** @odoo-module **/
// Copyright (C) 2019-Today: Druidoo (https://www.druidoo.io)
// @author: Iván Todorovich
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import {BarcodeParser} from "@barcodes/js/barcode_parser";
import {evaluateExpr} from "@web/core/py_js/py";
import {patch} from "@web/core/utils/patch";

patch(BarcodeParser, {
    barcodeRuleFields: [...BarcodeParser.barcodeRuleFields, "transform_expr"],
});

patch(BarcodeParser.prototype, {
    parseBarcodeNomenclature(barcode) {
        const result = super.parseBarcodeNomenclature(...arguments);
        if (!this.nomenclature || !result.value || result.type === "error") {
            return result;
        }
        const rules = this.nomenclature.rules || [];
        for (const rule of rules) {
            if (!rule.transform_expr || rule.type !== result.type) {
                continue;
            }
            let cur_barcode = barcode;
            if (
                rule.encoding === "ean13" &&
                this.check_encoding(barcode, "upca") &&
                this.nomenclature.upc_ean_conv in {upc2ean: "", always: ""}
            ) {
                cur_barcode = "0" + cur_barcode;
            } else if (
                rule.encoding === "upca" &&
                this.check_encoding(barcode, "ean13") &&
                barcode[0] === "0" &&
                this.nomenclature.upc_ean_conv in {ean2upc: "", always: ""}
            ) {
                cur_barcode = cur_barcode.substr(1, 12);
            }
            if (!this.check_encoding(cur_barcode, rule.encoding)) {
                continue;
            }
            const match = this.match_pattern(cur_barcode, rule.pattern, rule.encoding);
            if (match.match) {
                try {
                    result.original_value = result.value;
                    const new_value = evaluateExpr(rule.transform_expr, {
                        value: result.value,
                        code: result.code,
                        barcode: result.code,
                    });
                    if (typeof new_value !== "number") {
                        throw new TypeError(
                            `Transformed value should be a Number. Got: ${new_value} (${typeof new_value})`
                        );
                    }
                    result.value = new_value;
                } catch (err) {
                    console.error(
                        "Unable to apply transform expression:",
                        rule.transform_expr,
                        err
                    );
                }
                break;
            }
        }
        return result;
    },
});
