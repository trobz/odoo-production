from odoo import fields, models

# Member Manager only has read access to hr.employee (see
# security/ir.model.access.csv) and no hr.group_hr_user, but the standard
# Employees list/form view (chatter + activity widgets) reads all of these
# mail.activity.mixin / mail.thread fields unconditionally, which errors out
# without this group.
GROUPS = "hr.group_hr_user,foodcoop_data_role.group_Member_Manager"


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # mail.activity.mixin
    activity_ids = fields.One2many(groups=GROUPS)
    activity_state = fields.Selection(groups=GROUPS)
    activity_user_id = fields.Many2one(groups=GROUPS)
    activity_type_id = fields.Many2one(groups=GROUPS)
    activity_type_icon = fields.Char(groups=GROUPS)
    activity_date_deadline = fields.Date(groups=GROUPS)
    my_activity_date_deadline = fields.Date(groups=GROUPS)
    activity_summary = fields.Char(groups=GROUPS)
    activity_exception_decoration = fields.Selection(groups=GROUPS)
    activity_exception_icon = fields.Char(groups=GROUPS)

    # mail.thread mixin
    message_is_follower = fields.Boolean(groups=GROUPS)
    message_follower_ids = fields.One2many(groups=GROUPS)
    message_partner_ids = fields.Many2many(groups=GROUPS)
    message_ids = fields.One2many(groups=GROUPS)
    has_message = fields.Boolean(groups=GROUPS)
    message_needaction = fields.Boolean(groups=GROUPS)
    message_needaction_counter = fields.Integer(groups=GROUPS)
    message_has_error = fields.Boolean(groups=GROUPS)
    message_has_error_counter = fields.Integer(groups=GROUPS)
    message_attachment_count = fields.Integer(groups=GROUPS)
    message_main_attachment_id = fields.Many2one(groups=GROUPS)
