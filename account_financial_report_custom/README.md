# Account Financial Reports Custom

## Overview

This module provides customizations for OCA `account_financial_report` reports (Odoo
18), focused on improving the **General Ledger** output.

- Module name: `account_financial_report_custom`
- Version: `18.0.1.0.0`
- Category: Reporting
- License: AGPL-3

## Key Features

- Custom regrouping of General Ledger move lines to avoid duplicated / overly granular
  lines in the report.
  - Implemented by overriding `report.account_financial_report.general_ledger`.
  - Move lines are grouped by:
    - Date
    - Entry (move)
    - Account
    - Taxes description
    - Partner
    - Label / Ref
    - Cost center (analytic distribution)
    - Matching number (reconciliation)
    - Currency
- QWeb template adjustment for General Ledger lines
  (`report/templates/general_ledger.xml`).
  - Displays taxes, analytic distribution (cost center), analytic tags, matching number,
    and optional foreign currency columns.

## Dependencies

- `account_financial_report` (OCA)

## Installation

- Add this addon to your Odoo addons path.
- Update app list.
- Install module `Account Financial Reports Custom`.

## Usage

- Go to the Financial Reports provided by `account_financial_report`.
- Print / preview the **General Ledger** report.
- The report lines will be regrouped using the custom grouping logic from this module.

## Technical Notes

- The regrouping is performed in Python in `report/general_ledger.py`.
- The report layout customization is done via QWeb inheritance in
  `report/templates/general_ledger.xml`.
