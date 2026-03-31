# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)

from odoo import api, fields, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    department_id = fields.Many2one(
        string="Origin Department",
        comodel_name="res.country.department",
        help="Department of production",
    )

    @api.depends(
        "origin_description", "country_id", "department_id", "maker_description"
    )
    def _compute_pricetag_origin(self):
        for record in self:
            parts = []
            if record.country_id:
                parts.append(record.country_id.name.upper())
            if record.department_id:
                parts.append(record.department_id.name)
            if record.origin_description:
                parts.append(record.origin_description)
            if record.maker_description:
                parts.append(record.maker_description)
            record.pricetag_origin = " - ".join(filter(None, parts))

    @api.onchange("country_id")
    def _onchange_country_id(self):
        if self.country_id:
            if self.department_id and self.department_id.country_id != self.country_id:
                self.department_id = False

    @api.onchange("department_id")
    def _onchange_department_id(self):
        if self.department_id:
            self.country_id = self.department_id.country_id
        else:
            self.country_id = False

    @api.constrains("department_id", "country_id")
    def _check_origin_department_country(self):
        for record in self:
            if (
                record.department_id.country_id
                and record.department_id.country_id != record.country_id
            ):
                raise UserError(
                    self.env._(
                        "Department %s doesn't belong to %s.",
                        record.department_id.name,
                        record.country_id.name,
                    )
                )
