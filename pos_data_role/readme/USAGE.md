This module is automatically configured and does not require manual setup. Once installed, it grants Cashlogy configuration access to the appropriate roles.

**Affected Roles**:
- **POS Manager**: Users with this role will automatically have access to Cashlogy device configuration
- **Foodcoop Admin**: Users with this role will automatically have access to Cashlogy device configuration

**Installation Requirements**:
- The `foodcoop_data_role` module must be installed (defines the base roles)
- The `pos_automatic_cashdrawer_cashlogy` module must be installed (provides Cashlogy integration)
- Your cooperative must be using Cashlogy automatic cash drawer hardware

**To verify the permissions are correctly applied**:
1. Go to **Settings > Users & Companies > Roles**
2. Open either "POS Manager" or "Foodcoop Admin" role
3. Check the **Implied Permissions** tab
4. Verify that "POS Automatic Cashlogy Config" group is listed

**Access Cashlogy Settings** (for users with appropriate roles):
1. Go to **Point of Sale > Configuration > Point of Sale**
2. Open a POS configuration
3. Cashlogy-specific configuration options will be available

**Note**: If your cooperative does not use Cashlogy hardware, do not install this module.
