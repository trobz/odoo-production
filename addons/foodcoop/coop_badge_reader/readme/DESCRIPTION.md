# Description

The **Coop Badge Reader** module provides a web-based badge/QR code reader interface for cooperative membership management. It enables time clock operators to authenticate members via barcode scanning, log check-in/check-out events, and display cooperative membership status in real-time.

## Key Features

- **Badge Reader Interface**: Web-based interface accessible at `/badge_reader` route
- **Member Authentication**: Authenticate users via barcode/card scanning
- **Movement Logging**: Track and store member check-ins and check-outs ("in", "out", "wrong")
- **Cooperative State Display**: Color-coded visual feedback based on membership status
- **Audio Feedback**: Different sounds for different member states (success, warning, danger)
- **Alert System**: Notify employees when expected members check in
- **Grace Period Handling**: Automatically manage grace periods for suspended members
- **Badge Distribution Tracking**: Mark badges as distributed to members

## Cooperative States

The module maps Odoo cooperative states to Bootstrap-style visual states:

| Cooperative State | Visual State | Description |
|-------------------|--------------|-------------|
| up_to_date | Success (Green) | Member is in good standing |
| exempted | Success (Green) | Member is exempted |
| alert | Warning (Yellow) | Member has an alert |
| delay | Warning (Yellow) | Member has a delay |
| suspended | Danger (Red) | Member is suspended |
| not_concerned | Danger (Red) | Member not concerned |
| blocked | Danger (Red) | Member is blocked |
| unpayed | Danger (Red) | Member has unpaid fees |
| unsubscribed | Danger (Red) | Member is unsubscribed |

## Technical Stack

- **Backend**: Python/Odoo 18.0
- **Frontend**: OWL (Odoo Web Library) components
- **UI Framework**: Bootstrap 5 via Odoo's asset system
- **Dependencies**: `coop_shift`, `coop_membership`

## Module Structure

```
coop_badge_reader/
├── controllers/          # HTTP controllers for badge reader route
├── models/              # Partner, partner move, partner alert models
├── views/               # XML views and templates
├── security/            # Access control groups
├── data/                # Mail templates
├── static/src/
│   ├── app/             # Main OWL application
│   ├── components/      # Reusable OWL components
│   ├── sounds/          # Audio feedback files
│   └── tests/           # JavaScript unit tests
└── readme/              # Documentation files
```
