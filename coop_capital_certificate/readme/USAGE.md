## Generating Capital Certificates

1. Go to **Accounting > Reporting > Capital Certificate** (or use the wizard from the menu)
2. Configure the certificate generation parameters:
   - **Fiscal Year**: Select the year for the certificate (defaults to N-1)
   - **Partners**: Choose to generate for all partners or select specific partners
   - **Send Mail**: Enable to automatically send certificates via email, or disable to only create attachments

3. Click **Generate** to create the certificates

## Viewing Certificates

Certificates are stored and can be accessed from the partner view:

1. Go to **Contacts** and select a partner
2. Navigate to the **Capital Certificate** tab to view all certificates for that partner

## Configuration

1. Setting up Report Header and Signature

- Go to **Accounting > Configuration > Configuration**
- Configure the following fields:
   - **Report Header**: Text to display at the top of the certificate
   - **Signature Image**: Image to use as signature on the report

2. Email Template

The module includes an email template for sending certificates. You can customize it in **Email > Templates** by searching for the capital certificate template.

## Notes

- Each partner can only have one certificate per year (duplicate prevention)
- Certificates are generated based on capital subscription moves in the selected fiscal year
- The report uses the capital account defined in each fundraising category
