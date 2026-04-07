This module provides email validation functionality for partners.

## Features

- Generate a unique validation string for each partner
- Send email validation link to partners
- Validate email through a web link
- Display warning when email is not validated
- Allow resending validation email

## Configuration

1. Install the module
2. When a partner with an email is created, a validation email is automatically sent
3. The partner must click the validation link in the email to confirm their email address
4. If the email is not validated, a warning is displayed on the partner form
5. Users with "Partner Manager" group can resend the validation email

## Requirements

- This module depends on `coop_membership` module
