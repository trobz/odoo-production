This module extends the cooperative membership functionality by limiting the number of extensions a member can receive.

## Features

1. **Extension Limit**: Set a maximum number of extensions a member can receive when they are in cooperative states: alert, suspended, or delay.

2. **Configurable Settings**:
   - Enable/disable the extension limit feature
   - Set the maximum number of extensions (default: 6)
   - Choose which extension types are counted towards the limit

3. **Automatic Warning**: When a member reaches one extension before the limit, an automatic email notification is sent to warn them.

4. **Access Control**: The extension limit check is bypassed for shift managers.

## Technical Details

- Inherits from `shift.extension` model
- Adds `is_new` boolean field to track new extensions
- Extends `res.company` with extension limit settings
- Integrates with `res.config.settings` for configuration
- Depends on `coop_membership` and `coop_badge_reader` modules
