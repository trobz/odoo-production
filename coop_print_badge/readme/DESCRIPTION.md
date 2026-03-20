# Badge Printing Module

The `coop_print_badge` module enables printing of badges for cooperative members and their associated people. Badges are generated in a standard credit card format (ISO/IEC 7810 - 85.60 x 53.98 mm), optimized for use with Evolis Zenius card printers.

## Features

- **Badge Printing**: Generate printable badges with member photos, names, and barcode information
- **Automatic Reprint Triggers**: Automatically flag badges for reprinting when key partner information changes
- **Dual Badge Types**: Supports badges for both full members and associated people
- **Barcode Generation**: Includes EAN13 barcodes for each member/associated person
- **Distribution Tracking**: Track when badges are printed and physically distributed

## Badge Types

### Member Badges
Displays the member's photo, member number, and cooperative designation based on gender:
- "Coopérateur" (Male)
- "Coopératrice" (Female)
- "Coop" (Neutral)

### Associated People Badges
Displays the photo of associated people with their relationship number:
- "Rattaché n°" (Male)
- "Rattachée n°" (Female)
- "Rattaché(e) n°" (Neutral)

## Technical Specifications

- **Badge Dimensions**: 106mm x 68mm
- **Photo Size**: 47mm x 61mm
- **Barcode Format**: EAN13
- **Image Resolution**: 315x417px for badge-sized images
- **Printer Compatibility**: Optimized for Evolis Zenius card printers

## Dependencies

This module depends on:
- `coop_membership`: Core membership management
- `coop_shift`: Shift management and menu structure
- `base`: Base Odoo functionality
- `web`: Web reporting framework

## Access Rights

- **Print Badges**: Users with `group_membership_access_user` or `group_membership_see_associated_people`
- **View Badges to Print**: Users with `group_shift_manager`
- **View Badges to Distribute**: Users with `group_membership_bdm_lecture` or `group_membership_bdm_saisie`
