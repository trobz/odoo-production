from odoo import fields, models


class Project(models.Model):
    _inherit = "project.project"

    privacy_visibility = fields.Selection([
        ('followers', 'On invitation only'),
        ('employees', 'Visible by all employees'),
    ])
    project_categ_ids = fields.Many2many(
        'project.category', 'project_project_category_rel',
        'project_id', 'category_id', string='Categories')
