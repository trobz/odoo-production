This module customizes the website header layout specifically for food cooperative websites, providing better menu management and layout control.

**Key Features**:

1. **Force Invisible Menu Option**: Adds a `force_invisible` field to website menu items, allowing administrators to permanently hide specific menu entries without deleting them

2. **Contact Us Button Hidden**: Automatically hides the "Contact Us" button from the website header (useful when cooperatives manage contact through other channels or custom pages)

3. **Enhanced Header Layout**: Implements responsive CSS customizations that:
   - Prevents menu auto-hiding behavior
   - Enables menu item wrapping on large screens (≥992px)
   - Optimizes space distribution between logo, menu, and utility buttons
   - Ensures the navigation menu can grow and wrap as needed

4. **Automatic Setup**: Post-installation hook automatically marks `/contactus` menu items as force invisible

**Technical Implementation**:

- Extends `website.menu` model with visibility control
- Overrides QWeb header templates to modify CSS classes and hide contact button
- Provides responsive SCSS for flexible menu layout
- Includes migration script to apply settings to existing installations

**Use Cases**:

- Food cooperatives that want to hide standard Odoo menu items without losing them
- Sites with custom contact workflows that don't need the default "Contact Us" page
- Websites with many menu items that need wrapping behavior instead of auto-collapsing
- Customized navigation layouts for cooperative-specific needs

This module is specifically designed for food cooperative websites but can be adapted for other similar use cases.
