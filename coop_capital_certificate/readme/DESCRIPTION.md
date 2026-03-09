This module extends the `capital_subscription` functionality to provide a **Fiscal Certificate Report** for capital subscriptions.

## Features

- **Capital Certificate Wizard**: Generate fiscal certificate reports for partners who have purchased capital shares.
- **Year Selection**: Choose the fiscal year (defaults to previous year N-1).
- **Partner Selection**: Generate certificates for selected partners or all partners.
- **Email Automation**: Automatically send certificates via email to partners or create attachments for manual access.
- **Certificate Tracking**: Each certificate is linked to a partner and year, with a unique constraint to prevent duplicates.
- **Customizable Templates**: Uses email templates for report generation and sending.
- **Company Branding**: Reports use the company's external layout with customizable header and signature images.

## Configuration

Configure additional parameters in **Accounting > Configuration > Configuration**:
- Report header text
- Signature image

The wizard generates a PDF report for each partner that has capital fundraising moves in the selected year, based on the `capital_account_id` defined in the fundraising category.
