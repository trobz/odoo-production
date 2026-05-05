## Purpose

Customizes Point of Sale (POS) access rights to restrict order modifications after payment.

## Functionality

- Patches the POS order line to prevent quantity changes after payment
- Restricts users without "hasGroupDeleteOrder" permission from modifying paid orders
- Displays authorization error message when unauthorized modification is attempted
- Extends the base `pos_access_right` module functionality

## Dependencies

- `pos_access_right`: Base module for POS access right management

## License

LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
