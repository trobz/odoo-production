from odoo import api, fields, models

COLOR_HEX = {
    1: "#F06050",
    2: "#F4A460",
    3: "#F7CD1F",
    4: "#6CC1ED",
    5: "#814968",
    6: "#EB7E7F",
    7: "#2C8397",
    8: "#475577",
    9: "#D6145F",
    10: "#30C381",
    11: "#9365B8",
}


class ProjectCategory(models.Model):
    _name = "project.category"
    _description = "Project Category"

    name = fields.Char(required=True)
    color = fields.Integer(string="Color Index")
    color_code = fields.Char(compute="_compute_color_code")
    project_ids = fields.Many2many(
        "project.project",
        "project_project_category_rel",
        "category_id",
        "project_id",
    )

    @api.depends("color")
    def _compute_color_code(self):
        for categ in self:
            categ.color_code = COLOR_HEX.get(categ.color, "")
