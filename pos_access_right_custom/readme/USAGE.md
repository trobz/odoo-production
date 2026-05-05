## Features

- Prevents order line quantity changes after payments are registered
- Restricts modification based on user group permissions
- Shows clear error message for unauthorized actions

## How it works

1. When a user attempts to change the quantity of an order line
2. The system checks if:
   - The user has the "hasGroupDeleteOrder" permission
   - The order already has payments registered
3. If both conditions are met, the quantity change is blocked
4. An error message is displayed: "Change Order Value - Unauthorized function"

## Configuration

1. Install the `pos_access_right` module first
2. Install this `pos_access_right_custom` module
3. Assign the appropriate user groups to control who can modify paid orders
4. Users with "hasGroupDeleteOrder" permission will be blocked from changing quantities on paid orders

## Requirements

- Depends on `pos_access_right` module
