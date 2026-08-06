The "Roles for Foodcoop" module provides a comprehensive role-based access control
system for the Foodcoop platform. It defines multiple user roles with specific group
memberships to ensure proper segregation of duties and access control.

### Pre-defined Roles

This module includes 19 distinct roles covering all aspects of Foodcoop operations:

1. **Cashier**: Basic POS operations
2. **Member Manager**: Member lifecycle management
3. **Accountant**: Financial operations
4. **Inventory Manager**: Stock control
5. **Teamleader**: Shift coordination
6. **Purchaser**: Procurement tasks
7. **Purchase Manager**: Procurement management
8. **Foodcoop Admin**: Full system administration
9. **BDMLecture**: Read-only BDM access
10. **BDMPresence**: Attendance tracking
11. **BDMSaisie**: BDM data entry
12. **POS Manager**: POS management
13. **Subscription**: Subscription handling
14. **Communications Officer**: Marketing operations
15. **Communications Manager**: Marketing management
16. **Welcome Meeting Team**: Event coordination
17. **Member Accountant**: Restricted accounting
18. **BadgeReader**: Badge operations
19. **Staff**: General staff access

### Access Control

- Group-based permission management
- Menu visibility control
- View restriction capabilities
- Toolbar customization per role

### Integration

This module depends on and integrates with:

- base_user_role
- point_of_sale
- purchase
- stock
- coop_shift
- coop_membership
- And many other Foodcoop-specific modules
