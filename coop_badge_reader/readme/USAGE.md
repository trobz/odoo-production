## Accessing the Badge Reader

### URL Access

Once installed, the badge reader interface is available at:

```
https://your-domain.com/badge_reader
```

**Note:** Only users belonging to the **Coop Badge Reader / Time Clock** security group can access this page.

## Search Functionality

### Searching Members

Users can search for members using any of the following fields:

| Field | Description |
|-------|-------------|
| **Barcode** | Scan or enter the member's badge/barcode number |
| **Member number** | Search by base barcode identifier (barcode_base) |
| **Name** | Search by member name (triggers name_search) |

### Search Results

| Result | Behavior |
|--------|----------|
| **One match** | Display the partner form directly |
| **Multiple matches** | Display a list of matching partners for selection |
| **No match** | Play "not found" sound and display an error message |

### Search Filters

The search automatically filters to:
- Non-deceased partners (`is_deceased = false`)
- Members or associated people (`is_member = True` OR `is_associated_people = True`)

**Note:** The name search does not apply these filters (filters are commented out in the implementation).

## Partner Form

When a member is found, the partner form displays:

| Field | Description |
|-------|-------------|
| **Partner Image** | Photo of the member |
| **Partner Name** | Full name of the member |
| **Status** | Cooperative state with color-coded label |
| **Can Purchase** | Whether the partner is marked as a customer |
| **Warning/Error Message** | Displays if the partner has special conditions |

### Cooperative States

The following states may be displayed:

| State | Label | Color |
|-------|-------|-------|
| up_to_date | Up to date | Green |
| exempted | Exempted | Green |
| alert | Alert | Yellow |
| delay | Grace period granted | Yellow |
| suspended | Suspended | Red |
| not_concerned | Not concerned | Red |
| blocked | Blocked | Red |
| unpayed | Unpaid | Red |
| unsubscribed | Unsubscribed | Red |
| vacation | On leave | Red |

### Action Buttons

| Button | Action | Result |
|--------|--------|--------|
| **Enter** | Check member in | Logs "in" action, redirects to badge reader |
| **Do not enter** | Check member out | Logs "out" action, redirects to badge reader |
| **Error** | Report error | Logs "wrong" action, redirects to badge reader |
| **Badge distributed** | Mark badge as distributed | Available only if `badge_to_distribute` is True |

### Grace Period Behavior

- When a partner with **delay** status loads the form, a grace period is automatically applied
- A warning message displays: "A grace period until [date] or until your next service has been assigned to you. You may proceed with your shopping!"
- When a partner with **suspended** status loads the form with no available grace period:
  - A danger message displays: "We were unable to grant you a grace period; you must make up your services before doing your shopping."

## Partner List

When multiple partners match a search, a list view is displayed showing:

- Partner image
- Partner name
- Cooperative state (color-coded)
- Address information (street, city)

Click on any partner to view their details and take action.

## Move Logs

All badge reader actions are logged and stored in the back-office.

### Accessing Move Logs

1. Go to **Coop Shift** menu
2. Navigate to **Partner Moves**

### Logged Information

Each move log entry contains:

| Field | Description |
|-------|-------------|
| Partner | The member who performed the action |
| Action | Type of action: "in", "out", or "wrong" |
| Cooperative State | Member's cooperative state at time of action |
| Bootstrap State | Visual state: "success", "warning", or "danger" |
| Date | Timestamp of the action |

### Log Management Permissions

| User Group | Permissions |
|------------|-------------|
| User | View move logs |
| Time Clock | View logs + Log into badge reader app |
| Manager | Full access (view, create, update, delete logs) |

## Alert System

The module includes an alert system to notify employees when expected members check in.

### Creating an Alert

1. Go to **Coop Shift > Partner Alerts**
2. Click **Create**
3. Select the **Expected Member**
4. Select **Employees to Alert**
5. Set the **State** to "Open"

### Alert Notifications

When an expected member with an open alert checks in (action: "in"):
- An email notification is automatically sent to the designated employees
- The alert remains open until manually closed

### Alert Permissions

| User Group | Permissions |
|------------|-------------|
| User | View, create, update alerts |
| Access Alert | Full access to manage alerts |
| Manager | Full access to manage alerts |

## Audio Feedback

The module provides different sounds for various scenarios:

| Sound File | Trigger |
|------------|---------|
| res_partner_success | Partner with "success" state (up_to_date, exempted) |
| res_partner_warning | Partner with "warning" state (alert, delay) |
| res_partner_danger | Partner with "danger" state (suspended, blocked, etc.) |
| res_partner_not_found | No partner found matching search criteria |

## Technical Information

### Frontend Architecture

The frontend is built using OWL (Odoo Web Library):

| Component | Purpose |
|-----------|---------|
| `badgeReaderApp` | Main application managing state and navigation |
| `PartnerListComponent` | Displays list of matching partners |
| `PartnerFormComponent` | Displays partner details and action buttons |

### RPC Methods Used

| Method | Description |
|--------|-------------|
| `res.partner.searchRead()` | Search partners by barcode/barcode_base with filters |
| `res.partner.name_search()` | Search partners by name |
| `res.partner.log_move()` | Log member check-in/out/error action |
| `res.partner.action_grace_partner()` | Apply grace period for delayed members |
| `res.partner.set_badge_distributed()` | Mark badge as distributed |

### Display States

The app supports three main display states:

| State | Description |
|-------|-------------|
| main | Search interface with input fields |
| partner_list | List of multiple matching partners |
| partner_form | Detailed partner view with action buttons |

### Navigation Flow

```
Main Search Screen
    |
    +--[1 match]--> Partner Form --> [Action] --> Main Search Screen
    |
    +--[Multiple]--> Partner List --> [Select] --> Partner Form
    |
    +--[No match]--> Error Message --> Main Search Screen
```
