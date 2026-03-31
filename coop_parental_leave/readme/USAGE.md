## Features

### Parental Leave Creation

1. Navigate to **Shifts > Leaves** and create a new leave
2. Select the leave type "Congé Parental" (Parental Leave)
3. Fill in the required fields:
   - **Partner**: The cooperative member
   - **Start Date**: Leave start date
   - **Expected or Actual Birthdate**: Expected or actual birthdate of the child
4. The system automatically:
   - Sets the leave as a parental leave (`is_parental_leave`)
   - Calculates the default stop date (1 year from start date)
   - Shows warnings if the start date is more than 12 weeks before the expected birthdate

### Birth Certificate Management

- Members have **4 weeks** after the expected birthdate to provide the birth certificate
- The **Birth Certificate Provided** field tracks whether the certificate has been submitted
- Without a birth certificate, the leave is automatically marked as unsuccessful after 33 days

### Member Status During Parental Leave

The module automatically manages member status:

| Period | Status | Description |
|--------|--------|-------------|
| First 32 days after birth | Exempted | Member is exempt from shifts |
| After 32 days with birth certificate | Exempted until end | Continues exemption until leave end |
| After 32 days without certificate | Unsubscribed | Member is unsubscribed from team |

### Shared Parental Leave

- The **Shared Leave** option allows two cooperative members to share parental leave
- Use the **Shared With** field to select the second parent (must be a worker member)

### Email Notifications

The module sends automated emails at key stages:

1. **Leave Validation** - When parental leave is confirmed
2. **Birth Certificate Reminder** - 21 days after expected birthdate (if not provided)
3. **Leave Abandoned** - 33 days after expected birthdate (if still no certificate)

## Cron Jobs

The module includes scheduled actions:

- **Update member status based on Parental Leave**: Runs daily to update member forced status
- **Send Reminder Birth Certificate Parental Leave**: Runs daily to send reminder and abandoned emails

## Validation Rules

- Maximum leave duration: 24 months (even for multiple births)
- Start date cannot be more than 12 weeks before expected birthdate (warning shown)
- If both expected birthdate and start date are in the past, leave creation is blocked
- Birth certificate is required after the expected birthdate to validate the leave
