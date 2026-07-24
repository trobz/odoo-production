This module extends the foodcoop role system to grant POS Cashlogy automatic cash drawer configuration access to specific user roles.

**Cashlogy** is an automatic cash drawer device used in Point of Sale systems. This module specifically targets food cooperatives that use the Cashlogy hardware for automated cash management.

The module automatically grants configuration permissions for the Cashlogy device to:
- **POS Manager** role
- **Foodcoop Admin** role

This ensures that users with these roles can:
- Configure Cashlogy device settings in the POS
- Manage automatic cash drawer parameters
- Access Cashlogy-specific technical options

**Important**: This module should **only be installed** on food cooperative instances that are actively using Cashlogy automatic cash drawer devices. Installing it on systems without Cashlogy hardware is unnecessary.

The module depends on:
- `foodcoop_data_role`: Base role system for food cooperatives
- `pos_automatic_cashdrawer_cashlogy`: Cashlogy device integration
