from odoo import fields, models


class ProjectCategory(models.Model):
    _name = "project.category"
    _description = "Project Category"

    name = fields.Char(required=True)
    color = fields.Integer(string='Color Index')
    project_ids = fields.Many2many(
        'project.project', 'project_project_category_rel',
        'category_id', 'project_id'
    )
