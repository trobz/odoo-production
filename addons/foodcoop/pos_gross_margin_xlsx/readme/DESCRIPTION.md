# POS Gross Margin Report

This module allows generating a Gross Margin Report in XLSX format for Point of Sale data.

## Features

- Generate gross margin report in Excel format (XLSX)
- Calculate gross margin based on:
  - Pre-tax Net Sales during period
  - Inventory Value at beginning date
  - Net Purchases
  - Total available for Sale
  - Inventory Value at end date
  - Cost of Goods Sold (COGS)
  - Gross Margin
- Filter by product categories
- Date range selection

## Technical Details

- Depends on `coop_point_of_sale` and `report_xlsx` modules
- Uses `report.report_xlsx.abstract` for XLSX report generation
- Wizard-based interface for report generation
