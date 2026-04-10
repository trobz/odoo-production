# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64
import threading

from odoo import api, fields, models, tools
from odoo.tools.image import image_process


class ResPartner(models.Model):
    _inherit = "res.partner"

    image_badge = fields.Binary(
        "Badge-sized image",
        attachment=True,
        help="Badge-sized image of this contact. It is automatically "
        "resized as a 315x417px image, with aspect ratio preserved. "
        "Use this field in badge printing.",
    )

    # ### FUNCTIONS FOR DEFINING DEFAULT VALUES #########

    @api.model
    def _get_default_badge_to_print(self):
        trigger_fields = self._get_field_names_trigger_badge_reprint()
        fields_has_value = (
            trigger_fields
            and all([self[field_item] for field_item in trigger_fields])
            or False
        )
        return fields_has_value

    # ########## FIELDS DEFINITION ############

    badge_to_print = fields.Boolean(
        default=_get_default_badge_to_print,
    )
    updated_badges_info = fields.Boolean(
        "Updated Badges Information",
        compute="_compute_updated_badges_info",
        store=True,
    )

    # ######### COMPUTE FUNCTIONS ############

    @api.depends("badge_to_print", "is_member", "is_associated_people")
    def _compute_updated_badges_info(self):
        """
        @Function to compute the value of field updated_badges_info
        """
        for record in self:
            if record.badge_to_print and (
                record.is_member or record.is_associated_people
            ):
                record.updated_badges_info = True
            else:
                record.updated_badges_info = False

    # ###### RECORD OPERATION FUNCTIONS #########
    def untick_badges_to_print(self):
        for record in self:
            record.badge_to_print = False

    def write(self, vals):
        res = False
        fields_trigger_badge_reprint = self.env[
            "res.partner"
        ]._get_field_names_trigger_badge_reprint()
        for partner in self:
            partner_vals = vals.copy()
            # Update Badge Image
            if partner_vals.get("image_1920"):
                partner_vals.update(
                    {"image_badge": self.get_badge_image(partner_vals["image_1920"])}
                )
            for field_name in fields_trigger_badge_reprint:
                if (
                    field_name in partner_vals
                    and partner_vals.get(field_name) != partner[field_name]
                ):
                    partner_vals["badge_to_print"] = True
                    break
            if partner_vals.get("badge_to_print") and not partner._check_badge_to_print(
                vals
            ):
                partner_vals["badge_to_print"] = False
            res = super(ResPartner, partner).write(partner_vals)
        return res

    # ######## SUPPORTING FUNCTIONS ##########

    @api.model
    def _get_field_names_trigger_badge_reprint(self):
        """
        @Function to get a list of fields in Partner object which triggers
        badge to print
        """
        self = self.sudo()
        company = self.env.company
        fields_recs = company.reprint_change_field_ids
        return [
            field_item.name
            for field_item in fields_recs
            if field_item.name in self._fields
        ]

    @api.model_create_multi
    def create(self, vals_list):
        # Update Badge Image
        for vals in vals_list:
            if vals.get("image_1920"):
                vals.update(
                    {
                        "image_badge": self.get_badge_image(vals["image_1920"]),
                    }
                )
        return super().create(vals_list)

    @api.model
    def get_badge_image(self, src_image):
        src_image = base64.b64decode(src_image)
        image = image_process(
            src_image,
            size=(315, 417),
        )
        return base64.b64encode(image)

    def _check_badge_to_print(self, vals):
        self.ensure_one()
        trigger_fields = self._get_field_names_trigger_badge_reprint()
        fields_has_value = (
            trigger_fields
            and all(
                [
                    field_item in vals and vals[field_item] or self[field_item]
                    for field_item in trigger_fields
                ]
            )
            or False
        )
        #  S#25849: make sure the image is not the default one
        img_field = "image_1920"
        if img_field in trigger_fields and fields_has_value:
            default_img = self._get_default_image(
                self.type, self.is_company, self.parent_id.id
            )
            if img_field in vals:
                partner_img = vals[img_field]
            else:
                partner_img = self[img_field]
            if not partner_img or default_img == partner_img:
                return False
        return fields_has_value

    @api.model
    def _get_default_image(self, partner_type, is_company, parent_id):
        if getattr(threading.current_thread(), "testing", False) or self._context.get(
            "install_mode"
        ):
            return False

        image = False

        if partner_type == "other" and parent_id:
            parent = self.browse(parent_id)
            if parent.image_1920:
                image = base64.b64decode(parent.image_1920)

        if not image:
            img_paths = {
                "invoice": "base/static/img/money.png",
                "delivery": "base/static/img/truck.png",
            }
            img_path = img_paths.get(partner_type) or (
                "base/static/img/company_image.png"
                if is_company
                else "base/static/img/avatar.png"
            )
            with tools.file_open(img_path, "rb") as f:
                image = base64.b64encode(f.read()).decode()

        return image
