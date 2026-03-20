## Configuring Badge Reprint Triggers

The module allows administrators to define which partner fields, when modified, will automatically trigger badge reprinting.

### Steps to Configure

1. Navigate to: **Settings > Membership > Badge Printing**
2. Locate the **"Fields trigger badge reprinting"** field
3. Select the fields that should trigger a badge reprint when modified
4. Click **Save**

### Default Trigger Fields

By default, the following fields are configured to trigger reprinting:
- **Name** (`base.field_res_partner__name`)
- **Photo** (`base.field_res_partner__image_1920`)

### Recommended Fields to Trigger Reprinting

Consider adding these fields depending on your needs:

| Field | Description |
|-------|-------------|
| Name | When member changes their name |
| Photo | When profile picture is updated |
| Gender | When gender/title is changed |
| Barcode | When membership number changes |

## Technical Details

The configuration is stored as an `ir.config_parameter` with key `reprint_change_field_ids`. The value stores a list of field IDs as string representations.

### Field Selection Rules

- Only fields from the `res.partner` model can be selected
- Fields should represent information displayed on the badge
- Changing fields not in this list will not trigger automatic reprinting

## Paper Format Configuration

The module includes a pre-configured paper format for credit card-sized badges:

- **Format Name**: CEI 7810 - Credit Card
- **Dimensions**: 85.60 x 53.98 mm
- **Orientation**: Landscape

This format is automatically available when printing badges through the report action.
