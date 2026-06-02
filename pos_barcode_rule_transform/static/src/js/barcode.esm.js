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
    _getEffectiveBarcode(barcode, rule) {
        const conv = this.nomenclature.upc_ean_conv;
        if (
            rule.encoding === "ean13" &&
            this.check_encoding(barcode, "upca") &&
            conv in {upc2ean: "", always: ""}
        ) {
            return "0" + barcode;
        }
        if (
            rule.encoding === "upca" &&
            this.check_encoding(barcode, "ean13") &&
            barcode[0] === "0" &&
            conv in {ean2upc: "", always: ""}
        ) {
            return barcode.substr(1, 12);
        }
        return barcode;
    },

    _applyTransformExpr(parsed_result, rule) {
        if (!rule.transform_expr || !parsed_result.value) {
            return;
        }
        try {
            parsed_result.original_value = parsed_result.value;
            const new_value = evaluateExpr(rule.transform_expr, {
                value: parsed_result.value,
                code: parsed_result.code,
                barcode: parsed_result.code,
            });
            if (typeof new_value !== "number") {
                throw new TypeError(
                    `Transformed value should be a Number. Got: ${new_value} (${typeof new_value})`
                );
            }
            parsed_result.value = new_value;
        } catch (err) {
            console.error(
                "Unable to apply transform expression:",
                rule.transform_expr,
                err
            );
        }
    },

    // Override completely (no super) to apply transform_expr inline at
    // rule-match time — mirrors v12's try_rule approach where the same rule
    // that matches is also the one whose transform_expr is used.
    parseBarcodeNomenclature(barcode) {
        const parsed_result = {
            encoding: "",
            type: "error",
            code: barcode,
            base_code: barcode,
            value: 0,
        };
        if (!this.nomenclature) {
            return parsed_result;
        }
        const rules = this.nomenclature.rules || [];
        let currentBarcode = barcode;
        for (const rule of rules) {
            const cur_barcode = this._getEffectiveBarcode(currentBarcode, rule);
            if (!this.check_encoding(cur_barcode, rule.encoding)) {
                continue;
            }
            const match = this.match_pattern(cur_barcode, rule.pattern, rule.encoding);
            if (match.match) {
                if (rule.type === "alias") {
                    currentBarcode = rule.alias;
                    parsed_result.code = currentBarcode;
                    parsed_result.type = "alias";
                } else {
                    parsed_result.encoding = rule.encoding;
                    parsed_result.type = rule.type;
                    parsed_result.value = match.value;
                    parsed_result.code = cur_barcode;
                    parsed_result.base_code =
                        rule.encoding === "ean13"
                            ? this.sanitize_ean(match.base_code)
                            : match.base_code;
                    this._applyTransformExpr(parsed_result, rule);
                    return parsed_result;
                }
            }
        }
        return parsed_result;
    },
});
