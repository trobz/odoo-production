from odoo import fields, models


class Project(models.Model):
    _inherit = "project.project"

    privacy_visibility = fields.Selection(
        default="employees",
    )

    def get_kanban_categories(self):
        palette = [
            "#875A7B",
            "#F06050",
            "#F4A460",
            "#F7CD1F",
            "#6CC1ED",
            "#814968",
            "#EB7E7F",
            "#2C8397",
            "#475577",
            "#D6145F",
            "#30C381",
            "#9365B8",
        ]
        res = []
        for project in self:
            for tag in project.tag_ids:
                idx = int(tag.color or 0)
                res.append(
                    {
                        "name": tag.name,
                        "color": palette[idx % len(palette)],
                        "id": tag.id,
                    }
                )
        return res
