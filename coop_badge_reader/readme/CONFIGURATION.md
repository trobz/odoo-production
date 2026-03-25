## Module Dependencies

The **Coop Badge Reader** module requires the following dependencies:

| Module | Description |
|--------|-------------|
| `base` | Core Odoo functionality |
| `coop_shift` | Shift/rotating scheduling management |
| `coop_membership` | Cooperative membership management |

## Security Groups

The module defines four security groups for access control:

### Group Hierarchy

```
Manager (group_manager)
    └── Time Clock (group_time_clock)
            └── User (group_user)
                    └── (base permissions)

Access Alert (group_alert_entry_manager)
    └── User (group_user)
            └── (base permissions)
```

### Group Details

| Group | ID | Description | Implied Groups |
|-------|-----|-------------|----------------|
| **User** | `coop_badge_reader.group_user` | View move logs history | - |
| **Time Clock** | `coop_badge_reader.group_time_clock` | Use badge reader app | User |
| **Manager** | `coop_badge_reader.group_manager` | Full access to manage logs | Time Clock, User |
| **Access Alert** | `coop_badge_reader.group_alert_entry_manager` | Manage partner alerts | User |

## Model Access Rights

### res.partner.move

| Group | Read | Create | Write | Delete |
|-------|------|--------|-------|--------|
| User | Yes | No | No | No |
| Time Clock | Yes | Yes | No | No |
| Manager | Yes | Yes | Yes | Yes |

### res.partner.alert

| Group | Read | Create | Write | Delete | Unlink |
|-------|------|--------|-------|--------|--------|
| User | Yes | Yes | Yes | No | No |
| Time Clock | Yes | Yes | Yes | No | No |
| Manager | Yes | Yes | Yes | Yes | Yes |
| Alert Entry Manager | Yes | Yes | Yes | No | No |

### shift.extension

| Group | Read | Create | Write | Delete |
|-------|------|--------|-------|--------|
| User | Yes | No | No | No |
| Time Clock | Yes | No | No | No |
| Manager | Yes | Yes | Yes | Yes |

### shift.extension.type

| Group | Read | Create | Write | Delete |
|-------|------|--------|-------|--------|
| User | Yes | No | No | No |
| Time Clock | Yes | No | No | No |
| Manager | Yes | Yes | Yes | Yes |

## Partner Model Extensions

### Computed Fields

The module extends `res.partner` with the following computed fields:

| Field | Type | Description |
|-------|------|-------------|
| `next_shift_time` | Datetime | Next scheduled shift date and time |
| `bootstrap_cooperative_state` | Selection | Visual state (success/warning/danger) |
| `error_message` | Text | Error message for display |

### Model Methods

| Method | Description |
|--------|-------------|
| `log_move(action)` | Log a member movement (in/out/wrong) |
| `action_grace_partner()` | Apply grace period for suspended members |
| `set_badge_distributed()` | Mark badge as distributed |
| `update_boostrap_partner_state()` | Update the bootstrap cooperative state |

## Grace Period Configuration

The grace period functionality requires:

1. **Shift Extension Type** with `is_grace_period` = True
2. The extension type must have either:
   - `extension_method` = "to_next_regular_shift", or
   - `duration` > 0

### Creating a Grace Period Extension Type

1. Go to **Coop Shift > Configuration > Extension Types**
2. Create a new extension type
3. Enable **Grace Period** checkbox
4. Set the **Duration** (in days)
5. Configure the **Extension Method**

## Email Notifications

### Partner Alert Template

The module includes an email template for partner alert notifications:

- **Template ID**: `coop_badge_reader.email_template_partner_alert`
- **Trigger**: Automatically sent when an expected member with open alert checks in
- **Recipients**: Employees specified in the partner alert

## Partner Views

### Form View Extensions

The module adds fields to partner views:

| Field | View | Position |
|-------|------|----------|
| `next_shift_time` | Coop Shift Partner Form | After `date_delay_stop` |
| `bootstrap_cooperative_state` | Base Partner Form | Before `ref` field |

### Search Filters

The following filters are added to partner search:

| Filter Name | Domain |
|-------------|--------|
| Success Status | `bootstrap_cooperative_state = 'success'` |
| Warning Status | `bootstrap_cooperative_state = 'warning'` |
| Danger Status | `bootstrap_cooperative_state = 'danger'` |

## Menu Structure

### Badge Reader Menu

```
Coop Shift (root)
├── Partner Moves (res.partner.move)
├── Partner Alerts (res.partner.alert)
└── Configuration
    ├── Extension Types (shift.extension.type)
    └── Partner Moves Categories (if applicable)
```

## OWL Assets Configuration

The module defines custom assets for production:

```python
'coop_badge_reader.assets_prod': [
    'web._assets_helpers',
    'web._assets_primary_variables',
    'web._assets_frontend_helpers',
    'web.static/lib/jquery/jquery.js',
    'web/static/src/scss/pre_variables.scss',
    'web/static/lib/bootstrap/scss/_variables.scss',
    'web/static/lib/bootstrap/scss/_variables-dark.scss',
    'web.static/lib/bootstrap/scss/_maps.scss',
    'web._assets_bootstrap_frontend',
    'web._assets_bootstrap_backend',
    'web/static/lib/odoo_ui_icons/*',
    'web/static/lib/bootstrap/scss/_functions.scss',
    'web/static/lib/bootstrap/scss/_mixins.scss',
    'web/static/lib/bootstrap/scss/utilities/_api.scss',
    'web/static/src/libs/fontawesome/css/font-awesome.css',
    'web._assets_core',
    'coop_badge_reader/static/src/app/**/*',
    'coop_badge_reader/static/src/components/**/*',
]
```

## Demo Data

The module includes demo data for testing:

| File | Content |
|------|---------|
| `demo/res_groups.xml` | Demo user groups |
| `demo/res_users.xml` | Demo users |
| `demo/res_partner.xml` | Demo partners |

## Installation Checklist

1. [ ] Install required dependencies (`coop_shift`, `coop_membership`)
2. [ ] Install the `coop_badge_reader` module
3. [ ] Create users and assign appropriate security groups
4. [ ] Configure grace period extension type (if needed)
5. [ ] Set up partner alert email notifications
6. [ ] Test badge reader functionality
7. [ ] Configure firewall to allow access to `/badge_reader` route

## Troubleshooting

### User cannot access badge reader

- Verify user is member of **Coop Badge Reader / Time Clock** group
- Check user belongs to the correct database

### Grace period not working

- Ensure a shift extension type with `is_grace_period = True` exists
- Verify the extension type has valid duration or method

### Alert emails not sent

- Check email server configuration in Odoo
- Verify partner alert is in "Open" state
- Ensure expected member ID is set correctly
