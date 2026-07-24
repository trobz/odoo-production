**Installation**:

After installing this module:
- The "Contact Us" button in the website header will be automatically hidden
- The `/contactus` menu item will be marked as force invisible
- Header layout will be enhanced with custom CSS for better menu wrapping

**Using the Force Invisible Feature**:

To permanently hide any website menu item:

1. Go to **Website > Configuration > Menu**
2. Select the menu item you want to hide
3. Check the **Force Invisible** checkbox
4. Save the menu item

The menu will now be hidden from the website regardless of other visibility settings.

**Managing Header Menu Layout**:

The module automatically improves menu layout on larger screens (desktop/tablet):
- The navigation menu will wrap to multiple lines if needed instead of collapsing
- Logo stays at its natural width
- Menu items have flexible spacing and can grow to fill available space
- Utility items (if any) remain visible without being pushed to a new line

**Customizing the Contact Us Visibility**:

If you want to show the Contact Us button again:
1. Edit the QWeb template `website_coop_custom.header_call_to_action_hide_contactus`
2. Change `t-if="False"` to `t-if="True"` or remove the attribute
3. Update the website menu to uncheck **Force Invisible** for `/contactus`

**For Developers**:

The header CSS customizations apply when:
- Screen width is 992px or larger (Bootstrap large breakpoint)
- The header has the `coop_header_wrap` class (automatically added by this module)
- The `o_no_autohide_menu` class prevents automatic menu hiding

To customize the layout further:
- Edit `/static/src/scss/website_coop_custom.scss`
- Modify the `.coop_header_wrap #o_main_nav` ruleset
- Adjust flex properties for your specific layout needs

**Note**: The module includes both a post-init hook and a migration script to ensure the `/contactus` menu is hidden on both new installations and upgrades.
