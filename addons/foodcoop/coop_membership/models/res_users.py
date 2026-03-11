from odoo import api, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        """
        Function trigger to
            - Change the email of current user to the email of
            the assigned partner
        """
        self.login = self.partner_id and self.partner_id.email or ""

    def check_access_buttons(self, res_model):
        """
        Check group current user to hide buttons

        """
        presence_group = self.has_group("coop_membership.group_membership_bdm_presence")
        lecture_group = self.has_group("coop_membership.group_membership_bdm_lecture")
        saisie_group = self.has_group("coop_membership.group_membership_bdm_saisie")

        if not self or self._is_admin():
            return False
        elif res_model == "res.partner":
            if saisie_group:
                return "saisie_group_partner"
            if presence_group:
                return "presence_group_partner"
            if lecture_group:
                return "lecture_group_partner"
        elif res_model == "shift.shift":
            if presence_group:
                return "presence_group_shift"
            if lecture_group:
                return "lecture_group_shift"
            if saisie_group:
                return "saisie_group_shift"
        elif res_model == "shift.leave":
            if saisie_group:
                return "saisie_group_leave"
        # elif res_model == "shift.registration":
        #     if saisie_group:
        #         return 'saisie_group_registration'
        elif res_model == "shift.template.registration.line":
            if saisie_group:
                return "saisie_group_template_registration_line"
        elif res_model == "shift.extension":
            if saisie_group:
                return "saisie_group_extension"
        else:
            return False

    def check_access_ui(self, res_model):
        """
        Check group current user to hide buttons / bars
        @return: dict({
            # For Form
            "actionMenuItems": True / False,
            "o_mail_Chatter_top": True / False,
            "can_Create_Edit": True / False,

            # For list
            "cogMenuImport": True / False,
            # For list: when select the checkbox
            "actionMenuItems": True / False,
        })

        """
        result = self.check_access_buttons(res_model)
        resp = {
            "actionMenuItems": True,
            "o_mail_Chatter_top": True,
            "can_Create_Edit": True,
            "cogMenuImport": True,
            "result": result,
        }
        if result == "lecture_group_partner":
            resp["actionMenuItems"] = False
            resp["o_mail_Chatter_top"] = False
            resp["can_Create_Edit"] = False
        elif result == "presence_group_partner":
            resp["actionMenuItems"] = False
            resp["o_mail_Chatter_top"] = False
            resp["can_Create_Edit"] = False
        elif result == "saisie_group_partner":
            resp["actionMenuItems"] = False
            resp["o_mail_Chatter_top"] = False
        elif result == "presence_group_shift":
            resp["actionMenuItems"] = False
            resp["o_mail_Chatter_top"] = False
            resp["can_Create_Edit"] = True
        elif result == "saisie_group_shift":
            resp["actionMenuItems"] = False
            resp["o_mail_Chatter_top"] = False
        elif result == "saisie_group_leave":
            resp["actionMenuItems"] = False
            resp["o_mail_Chatter_top"] = False
        # else:
        #     resp["actionMenuItems"] = True
        #     resp["o_mail_Chatter_top"] = True
        #     resp["can_Create_Edit"] = True
        if result:
            resp["cogMenuImport"] = False
        self.check_access_ui_super_groups(resp)
        return resp

    def check_access_ui_super_groups(self, resp):
        if self.has_group("coop_membership.group_membership_chatter_topbar"):
            resp["o_mail_Chatter_top"] = True
        if self.has_group("coop_membership.group_membership_action_sidebar"):
            resp["actionMenuItems"] = True
        if self.has_group("base_import_security_group.group_import_csv"):
            # F#T66616 - [Chaudron] Membres/Contacts: show import btn
            # for users in this group
            resp["cogMenuImport"] = True
