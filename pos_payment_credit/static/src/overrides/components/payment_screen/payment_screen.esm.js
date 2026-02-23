/* License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

import {AlertDialog} from "@web/core/confirmation_dialog/confirmation_dialog";
import {PaymentScreen} from "@point_of_sale/app/screens/payment_screen/payment_screen";
import {_t} from "@web/core/l10n/translation";
import {ask} from "@point_of_sale/app/store/make_awaitable_dialog";
import {patch} from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
    setup() {
        super.setup(...arguments);
        // Auto-apply credit on initial payment screen load
        this.autoApplyCreditPayment();
    },

    /**
     * Override to handle credit payment method as a payment terminal
     */
    async addNewPaymentLine(paymentMethod) {
        const result = await super.addNewPaymentLine(...arguments);

        // If this is a credit payment method, process it as a terminal
        if (paymentMethod.use_payment_terminal === "credit") {
            const order = this.currentOrder;
            const partner = order.partner_id;

            if (!partner) {
                const confirmed = await ask(this.dialog, {
                    title: _t("Customer Required"),
                    body: _t("Please select a customer to use credit payment."),
                });
                if (!confirmed) {
                    return false;
                }
                this.pos.selectPartner();
            }

            // Get the payment line that was just added
            const paymentLine = order.payment_ids?.find(
                (line) =>
                    line.payment_method_id?.id === paymentMethod.id && !line.is_done()
            );

            if (paymentLine) {
                await this.processCreditPaymentLine(paymentLine);
            }
        }

        return result;
    },

    /**
     * Process credit payment line through the controller
     * @param {Object} paymentLine - The payment line to process
     */
    async processCreditPaymentLine(paymentLine) {
        const order = this.currentOrder;
        const partner = order.partner_id;
        if (!partner) {
            order.payment_ids = order.payment_ids.filter(
                (line) => line !== paymentLine
            );
            return;
        }
        const amount = paymentLine.amount;

        // Check if this is a refund
        const isRefund = amount < 0;

        // Validate credit balance for payments (not refunds)
        if (!isRefund && partner.credit_amount < amount) {
            await this.dialog.add(AlertDialog, {
                title: _t("Insufficient Credit"),
                body: _t(
                    "Customer has insufficient credit balance. Available: %s, Required: %s",
                    this.env.utils.formatCurrency(partner.credit_amount),
                    this.env.utils.formatCurrency(amount)
                ),
            });
            // Remove the payment line
            order.payment_ids = order.payment_ids.filter(
                (line) => line !== paymentLine
            );
            return;
        }

        // Confirm the action
        const confirmMessage = isRefund
            ? _t(
                  "Process refund of %s to customer credit?\n\nCurrent balance: %s\nNew balance: %s",
                  this.env.utils.formatCurrency(Math.abs(amount)),
                  this.env.utils.formatCurrency(partner.credit_amount),
                  this.env.utils.formatCurrency(
                      partner.credit_amount + Math.abs(amount)
                  )
              )
            : _t(
                  "Pay %s with customer credit?\n\nCurrent balance: %s\nRemaining: %s",
                  this.env.utils.formatCurrency(amount),
                  this.env.utils.formatCurrency(partner.credit_amount),
                  this.env.utils.formatCurrency(partner.credit_amount - amount)
              );

        const confirmed = await ask(this.dialog, {
            title: isRefund
                ? _t("Confirm Refund to Credit")
                : _t("Confirm Credit Payment"),
            body: confirmMessage,
        });

        if (!confirmed) {
            // Remove the payment line if not confirmed
            order.payment_ids = order.payment_ids.filter(
                (line) => line !== paymentLine
            );
            return;
        }

        // Process the payment through the controller
        const result = await this.pos.processCreditPayment(paymentLine);

        if (result.status === "success") {
            // Payment succeeded - paymentLine is already marked as done in processCreditPayment
            if (order.get_due() <= 0) {
                if (this._creditAutoValidateInProgress) {
                    return;
                }
                this._creditAutoValidateInProgress = true;
                try {
                    await this.validateOrder(true);
                } finally {
                    this._creditAutoValidateInProgress = false;
                }
            } else {
                this.render();
            }
        } else {
            await this.dialog.add(AlertDialog, {
                title: _t("Payment Failed"),
                body:
                    result.error ||
                    _t("An error occurred while processing the payment."),
            });
            // Remove the payment line on failure
            order.payment_ids = order.payment_ids.filter(
                (line) => line !== paymentLine
            );
        }
    },

    /**
     * Override validateOrder to ensure credit payments are processed
     */
    async validateOrder(isForceValidate) {
        const order = this.currentOrder;

        // Check if there are any credit payment lines that haven't been processed
        const unprocessedCreditPayments =
            order.payment_ids?.filter(
                (line) =>
                    line.payment_method_id?.use_payment_terminal === "credit" &&
                    !line.is_done()
            ) || [];

        // Auto-process credit payments that were auto-applied
        if (unprocessedCreditPayments.length > 0) {
            for (const paymentLine of unprocessedCreditPayments) {
                // If this payment method has auto_apply enabled, process automatically
                if (paymentLine.payment_method_id?.auto_apply_credit_amount) {
                    // Process without confirmation dialog
                    await this.processAutoCreditPaymentLine(paymentLine);
                } else {
                    // Manual credit payments require confirmation
                    await this.dialog.add(AlertDialog, {
                        title: _t("Unprocessed Credit Payments"),
                        body: _t(
                            "Please process all credit payments before validating the order."
                        ),
                    });
                    return;
                }
            }
        }

        return await super.validateOrder(isForceValidate);
    },

    /**
     * Process auto-applied credit payment line without confirmation
     * @param {Object} paymentLine - The payment line to process
     */
    async processAutoCreditPaymentLine(paymentLine) {
        const order = this.currentOrder;
        const partner = order.partner_id;
        const amount = paymentLine.amount;

        // Validate credit balance
        if (partner.credit_amount < amount) {
            await this.dialog.add(AlertDialog, {
                title: _t("Insufficient Credit"),
                body: _t(
                    "Customer has insufficient credit balance. Available: %s, Required: %s",
                    this.env.utils.formatCurrency(partner.credit_amount),
                    this.env.utils.formatCurrency(amount)
                ),
            });
            // Remove the payment line
            order.payment_ids = order.payment_ids.filter(
                (line) => line !== paymentLine
            );
            throw new Error("Insufficient credit");
        }

        // Process the payment through the controller silently
        const result = await this.pos.processCreditPayment(paymentLine);

        if (result.status !== "success") {
            await this.dialog.add(AlertDialog, {
                title: _t("Payment Failed"),
                body:
                    result.error ||
                    _t("An error occurred while processing the payment."),
            });
            // Remove the payment line on failure
            order.payment_ids = order.payment_ids.filter(
                (line) => line !== paymentLine
            );
            throw new Error(result.error);
        }
    },

    /**
     * Auto-apply credit payment if conditions are met
     */
    autoApplyCreditPayment() {
        const order = this.currentOrder;
        const partner = order.partner_id;

        if (!partner || partner.credit_amount <= 0) {
            return;
        }

        // Find credit payment methods with auto_apply enabled
        const autoCreditMethods = this.payment_methods_from_config.filter(
            (pm) => pm.use_payment_terminal === "credit" && pm.auto_apply_credit_amount
        );

        if (autoCreditMethods.length === 0) {
            return;
        }

        // Check if credit payment is already applied
        const existingCreditPayment = order.payment_ids?.find(
            (line) =>
                line.payment_method_id?.use_payment_terminal === "credit" &&
                !line.is_done()
        );

        if (existingCreditPayment) {
            // Update existing credit payment amount if needed
            const dueAmount = order.get_due(existingCreditPayment);
            const optimalAmount = Math.min(partner.credit_amount, dueAmount);

            if (optimalAmount > 0 && existingCreditPayment.amount !== optimalAmount) {
                existingCreditPayment.set_amount(optimalAmount);
                this.render();
            }
            // Already has credit payment
            return;
        }

        // Calculate amount to apply (min of available credit and order due)
        const dueAmount = order.get_due();
        if (dueAmount <= 0) {
            // Order is fully paid
            return;
        }

        const creditToApply = Math.min(partner.credit_amount, dueAmount);
        // Use first auto-apply method
        const paymentMethod = autoCreditMethods[0];

        // Add the credit payment line without triggering terminal processing
        const newPaymentline = order.add_paymentline(paymentMethod);
        newPaymentline.set_amount(creditToApply);

        // Mark as pending for user confirmation
        // Don't auto-process, let validateOrder handle it
        this.render();
    },
});
