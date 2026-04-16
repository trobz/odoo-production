This module provides functionality to export account move lines from Odoo to external accounting software.

Features
========

- Export account move lines to XLSX format
- Filter by date range, journals, partners, and invoices
- Group move lines by configurable fields
- Configure custom export fields and formats
- Track export status with exported flag on moves
- Support multiple export configurations
- Attach generated files to export records

Configuration
=============

You can configure export settings at:

*Accounting > Journals*
-----------------------
- Set Export Code per journal (used in exported file)

*Accounting > Exports > Export Configuration*
---------------------------------------------
- Create multiple export configurations
- Set default configuration
- Configure fields to export
- Choose credit/debit format (01, DC, +-, -+)

Partners can have custom receivable/payable accounts for export:
*Contacts > select partner > Accounting tab*
- Account Receivable (software)
- Account Payable (software)

