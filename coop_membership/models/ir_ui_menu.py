from odoo import models

GROUP_BDM_LECTURE = "coop_membership.group_membership_bdm_lecture"
GROUP_BDM_PRESENCE = "coop_membership.group_membership_bdm_presence"
GROUP_BDM_SAISIE = "coop_membership.group_membership_bdm_saisie"

BDM_HIDDEN_MENUS = {
    # Hidden for Lecture and Presence, visible to Saisie.
    "coop_shift.menu_shift_shift": (GROUP_BDM_LECTURE, GROUP_BDM_SAISIE),
    "coop_membership.menu_shift_seats_available": (GROUP_BDM_LECTURE, GROUP_BDM_SAISIE),
    # Hidden for Lecture only, visible to Presence and Saisie.
    "coop_membership.menu_shift_attendance_entry": (
        GROUP_BDM_LECTURE,
        GROUP_BDM_PRESENCE,
    ),
    # Hidden for Presence only, visible to Lecture (its only menu) and Saisie.
    "coop_shift.menu_shift_registration_exchanges": (
        GROUP_BDM_PRESENCE,
        GROUP_BDM_SAISIE,
    ),
}

# Only root menu BDM Lecture/Presence/Saisie are allowed to see.
BDM_LECTURE_ALLOWED_ROOT_MENU_XMLID = "coop_shift.shift_main_menu"


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    def _check_permission(self, menu_xmlid):
        """Return True if `menu_xmlid` must be hidden from the current user.

        Looks up the (from_group, up_to_excluded_group) range registered in
        BDM_HIDDEN_MENUS: the menu is hidden if the user holds `from_group`
        and does not hold `up_to_excluded_group` (if any). Admin is never
        restricted.
        """
        user = self.env.user
        if user._is_admin():
            return False
        restriction = BDM_HIDDEN_MENUS.get(menu_xmlid)
        if not restriction:
            return False
        from_group, up_to_excluded_group = restriction
        if not user.has_group(from_group):
            return False
        if up_to_excluded_group and user.has_group(up_to_excluded_group):
            return False
        return True

    def _is_bdm_profile(self):
        """Return True for any BDM role (Lecture, Presence or Saisie).

        BDM Presence and BDM Saisie both imply BDM Lecture, so checking the
        Lecture group alone covers all three profiles. Admin is excluded.
        """
        user = self.env.user
        if user._is_admin():
            return False
        return user.has_group(GROUP_BDM_LECTURE)

    def _load_menus_blacklist(self):
        blacklist = super()._load_menus_blacklist()
        for xmlid in BDM_HIDDEN_MENUS:
            if self._check_permission(xmlid):
                menu = self.env.ref(xmlid, raise_if_not_found=False)
                if menu:
                    blacklist.append(menu.id)
        return blacklist

    def get_user_roots(self):
        roots = super().get_user_roots()
        if self._is_bdm_profile():
            members_root = self.env.ref(
                BDM_LECTURE_ALLOWED_ROOT_MENU_XMLID, raise_if_not_found=False
            )
            if members_root and members_root in roots:
                return members_root
        return roots
