## Printing Badges

### For Shift Managers

1. Go to **Members > Reports > Badges**
2. A list of partners with pending badge updates will be displayed
3. Select the partners you want to print badges for
4. Click **Print Badge** from the action dropdown
5. A PDF document will be generated with badges in credit card format
6. Print the badges on your card printer

### For Badge Distribution Staff

1. Go to **Members > Members > Badges**
2. View partners marked for badge distribution
3. When physically handing out badges, update the **Badge Distribution Date** field
4. This marks the badge as distributed

## Understanding Badge Status

### Badge To Print
Automatically set to `True` when:
- A trigger field (configured in settings) is modified
- All trigger fields have valid values

### Updated Badges Info
Computed field that shows `True` when:
- `badge_to_print` is checked AND
- Partner is a member OR associated person

### Badge To Distribute
Computed field that shows `True` when:
- `badge_print_date` exists AND
- It's more recent than `badge_distribution_date` (or no distribution date set)

## Badge Print Workflow

```
1. Partner Information Updated
         ↓
2. Trigger Field Detected
         ↓
3. Badge To Print = True
         ↓
4. Updated Badges Info = True
         ↓
5. Manager Reviews & Prints Badge
         ↓
6. Badge To Print = False
         ↓
7. Badge Print Date Updated
         ↓
8. Badge To Distribute = True
         ↓
9. Staff Distributes Badge
         ↓
10. Badge Distribution Date Set
```

## Bulk Badge Printing

To print multiple badges at once:

1. Navigate to the Badges list view
2. Use filters to find partners needing badge updates
3. Select multiple records using the checkboxes
4. Click **Action > Print Badge**
5. All selected badges will be included in a single PDF

## Troubleshooting

### Badge Image Not Showing
- Ensure the partner has a photo uploaded (`Image` field in Contact form)
- The module automatically resizes photos to badge format (315x417px)

### Barcode Not Scanning
- Verify `barcode_base` field contains a valid number
- EAN13 barcodes require 12 digits

### Badge Not Triggering Reprint
- Check that the modified field is in the trigger list in Settings
- Ensure all trigger fields have values for the partner
