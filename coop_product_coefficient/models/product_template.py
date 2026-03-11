# Copyright (C) 2015-Today: Smile (<http://www.smile.fr>)
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# Copyright (C) 2012-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools import float_round


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # Column Section
    list_price = fields.Float(digits="Product Sale Price")
    standard_price = fields.Float(digits="Product Sale Price")

    coeff1_id = fields.Many2one(
        comodel_name="product.coefficient", string="Coefficient 1"
    )
    incl_in_standard_price_1 = fields.Boolean(
        string="Include in Standard Price (Coefficient 1)",
        default=False,
        help="""If you check this
        box, this coefficient will be used to calculate the standard price of
        the product""",
    )
    coeff2_id = fields.Many2one(
        comodel_name="product.coefficient", string="Coefficient 2"
    )
    incl_in_standard_price_2 = fields.Boolean(
        string="Include in Standard Price (Coefficient 2)",
        default=False,
        help="""If you check this
        box, this coefficient will be used to calculate the standard price of
        the product""",
    )
    coeff3_id = fields.Many2one(
        comodel_name="product.coefficient", string="Coefficient 3"
    )
    incl_in_standard_price_3 = fields.Boolean(
        string="Include in Standard Price (Coefficient 3)",
        default=False,
        help="""If you check this
        box, this coefficient will be used to calculate the standard price of
        the product""",
    )
    coeff4_id = fields.Many2one(
        comodel_name="product.coefficient", string="Coefficient 4"
    )
    incl_in_standard_price_4 = fields.Boolean(
        string="Include in Standard Price (Coefficient 4)",
        default=False,
        help="""If you check this
        box, this coefficient will be used to calculate the standard price of
        the product""",
    )
    coeff5_id = fields.Many2one(
        comodel_name="product.coefficient", string="Coefficient 5"
    )
    incl_in_standard_price_5 = fields.Boolean(
        string="Include in Standard Price (Coefficient 5)",
        default=False,
        help="""If you check this
        box, this coefficient will be used to calculate the standard price of
        the product""",
    )
    coeff6_id = fields.Many2one(
        comodel_name="product.coefficient", string="Coefficient 6"
    )
    incl_in_standard_price_6 = fields.Boolean(
        string="Include in Standard Price (Coefficient 6)",
        default=False,
        help="""If you check this
        box, this coefficient will be used to calculate the standard price of
        the product""",
    )
    coeff7_id = fields.Many2one(
        comodel_name="product.coefficient", string="Coefficient 7"
    )
    incl_in_standard_price_7 = fields.Boolean(
        string="Include in Standard Price (Coefficient 7)",
        default=False,
        help="""If you check this
        box, this coefficient will be used to calculate the standard price of
        the product""",
    )
    coeff8_id = fields.Many2one(
        comodel_name="product.coefficient", string="Coefficient 8"
    )
    incl_in_standard_price_8 = fields.Boolean(
        string="Include in Standard Price (Coefficient 8)",
        default=False,
        help="""If you check this
        box, this coefficient will be used to calculate the standard price of
        the product""",
    )
    coeff9_id = fields.Many2one(
        comodel_name="product.coefficient", string="Coefficient 9"
    )
    incl_in_standard_price_9 = fields.Boolean(
        string="Include in Standard Price (Coefficient 9)",
        default=False,
        help="""If you check this
        box, this coefficient will be used to calculate the standard price of
        the product""",
    )
    base_price = fields.Float(
        compute="_compute_base_price",
        store=True,
        digits="Product Price",
        help="Base Price is the Sale Price of your Supplier.\n"
        "If product is sold by many suppliers, the first one is selected.\n"
        "If a supplier sell the product with different prices, the bigger"
        " price is used.\n\n"
        "If The supplier info belong an end date, the base price will be"
        " updated nightly, by a cron task.",
    )
    alternative_base_price_sale = fields.Float(
        string="Alternative Base Price for Sale Price",
        help="This alternative base price will be used instead of the Base"
        " Price, if defined.",
    )
    alternative_base_price_standard = fields.Float(
        string="Alternative Base Price for Standard Price",
        help="This alternative base price will be used instead of the Base"
        " Price, if defined.",
    )
    coeff1_inter = fields.Float(
        string="With Coefficient 1",
        compute="_compute_coeff1_inter",
        store=True,
    )
    coeff2_inter = fields.Float(
        string="With Coefficient 2",
        compute="_compute_coeff2_inter",
        store=True,
    )
    coeff3_inter = fields.Float(
        string="With Coefficient 3",
        compute="_compute_coeff3_inter",
        store=True,
    )
    coeff4_inter = fields.Float(
        string="With Coefficient 4",
        compute="_compute_coeff4_inter",
        store=True,
    )
    coeff5_inter = fields.Float(
        string="With Coefficient 5",
        compute="_compute_coeff5_inter",
        store=True,
    )
    coeff6_inter = fields.Float(
        string="With Coefficient 6",
        compute="_compute_coeff6_inter",
        store=True,
    )
    coeff7_inter = fields.Float(
        string="With Coefficient 7",
        compute="_compute_coeff7_inter",
        store=True,
    )
    coeff8_inter = fields.Float(
        string="With Coefficient 8",
        compute="_compute_coeff8_inter",
        store=True,
    )
    coeff9_inter = fields.Float(
        string="With Coefficient 9",
        compute="_compute_coeff9_inter",
        store=True,
    )

    coeff1_inter_sp = fields.Float(
        string="With Supplier Discount Coefficient",
        compute="_compute_coeff1_inter",
        store=True,
    )
    coeff2_inter_sp = fields.Float(
        string="With Shipping Coefficient",
        compute="_compute_coeff2_inter",
        store=True,
    )
    coeff3_inter_sp = fields.Float(
        string="With Loss Coefficient",
        compute="_compute_coeff3_inter",
        store=True,
    )
    coeff4_inter_sp = fields.Float(
        string="With Coefficient 4 (Cost)",
        compute="_compute_coeff4_inter",
        store=True,
    )
    coeff5_inter_sp = fields.Float(
        string="With Coefficient 5 (Cost)",
        compute="_compute_coeff5_inter",
        store=True,
    )
    coeff6_inter_sp = fields.Float(
        string="With Coefficient 6 (Cost)",
        compute="_compute_coeff6_inter",
        store=True,
    )
    coeff7_inter_sp = fields.Float(
        string="With Coefficient 7 (Cost)",
        compute="_compute_coeff7_inter",
        store=True,
    )
    coeff8_inter_sp = fields.Float(
        string="With Coefficient 8 (Cost)",
        compute="_compute_coeff8_inter",
        store=True,
    )
    coeff9_inter_sp = fields.Float(
        string="With Margin Coefficient",
        compute="_compute_coeff9_inter",
        store=True,
    )
    theoritical_price = fields.Float(
        string="Theoritical Price VAT Incl.",
        compute="_compute_theoritical_price",
        store=True,
        digits="Product Sale Price",
    )
    has_theoritical_price_different = fields.Boolean(
        store=True,
        compute="_compute_has_theoritical_price_different",
    )
    has_theoritical_cost_different = fields.Boolean(
        store=True,
        compute="_compute_has_theoritical_cost_different",
    )
    theoritical_warning_label = fields.Char(
        string="Label warning", compute="_compute_theoritical_price", store=True
    )

    # Custom Section
    def recompute_base_price(self):
        self._compute_base_price()

    def use_theoritical_price(self):
        for template in self:
            template.with_context(skip_price_update=True).write(
                {"list_price": template.theoritical_price}
            )
        return True

    def use_theoritical_cost(self):
        for template in self:
            template.with_context(skip_price_update=True).write(
                {"standard_price": template.coeff9_inter_sp}
            )
        return True

    @api.model
    def recompute_base_price_batch(self, template_ids):
        self.browse(template_ids).recompute_base_price()
        return True

    @api.model
    def cron_recompute_base_price(self):
        auto_update_base_price = self.get_auto_update_base_price()
        if auto_update_base_price:
            template_ids = self.search([]).ids
            batch_size = 100
            template_obj = self.env["product.template"]
            for i in range(0, len(template_ids), batch_size):
                batch_ids = template_ids[i : i + batch_size]
                template_obj.with_delay().recompute_base_price_batch(batch_ids)

    # Compute Section
    @api.depends(
        "product_variant_ids",
        "uom_id",
        "uom_po_id",
        "seller_ids.price",
        "seller_ids.product_uom",
        "seller_ids.discount",
    )
    def _compute_base_price(self):
        # TODO IMPME. Compute with discount, depending on
        # product_supplierinfo_discount
        selected_vendor = self._context.get("selected_vendor", False)
        for template in self:
            base_price = 0.0
            if template.product_variant_ids:
                # We set a high quantity to avoid to skip
                seller = template.product_variant_ids[0]._select_seller(
                    partner_id=selected_vendor,
                    quantity=10000.0,
                )
                if seller:
                    if seller.product_uom.id == template.uom_id.id:
                        base_price = seller.price * (100 - seller.discount) / 100
                    else:
                        base_price = (
                            (seller.price / seller.product_uom.factor_inv)
                            * template.uom_id.factor_inv
                            * (100 - seller.discount)
                            / 100
                        )
            template.base_price = base_price

    @api.depends(
        "alternative_base_price_standard",
        "alternative_base_price_sale",
        "base_price",
        "coeff1_id.operation_type",
        "coeff1_id.value",
        "incl_in_standard_price_1",
    )
    def _compute_coeff1_inter(self):
        coefficient_obj = self.env["product.coefficient"]
        for template in self:
            if template.alternative_base_price_sale:
                base_price_sale = template.alternative_base_price_sale
            else:
                base_price_sale = template.base_price
            if template.alternative_base_price_standard:
                base_price_standard = template.alternative_base_price_standard
            else:
                base_price_standard = template.base_price
            template.coeff1_inter = coefficient_obj.compute_price(
                template.coeff1_id, base_price_sale
            )
            if template.incl_in_standard_price_1:
                template.coeff1_inter_sp = coefficient_obj.compute_price(
                    template.coeff1_id, base_price_standard
                )
            else:
                template.coeff1_inter_sp = base_price_standard

    @api.depends(
        "coeff1_inter",
        "coeff2_id.operation_type",
        "coeff2_id.value",
        "incl_in_standard_price_2",
    )
    def _compute_coeff2_inter(self):
        coefficient_obj = self.env["product.coefficient"]
        for template in self:
            template.coeff2_inter = coefficient_obj.compute_price(
                template.coeff2_id, template.coeff1_inter
            )
            if template.incl_in_standard_price_2:
                template.coeff2_inter_sp = coefficient_obj.compute_price(
                    template.coeff2_id, template.coeff1_inter_sp
                )
            else:
                template.coeff2_inter_sp = template.coeff1_inter_sp

    @api.depends(
        "coeff2_inter",
        "coeff3_id.operation_type",
        "coeff3_id.value",
        "incl_in_standard_price_3",
    )
    def _compute_coeff3_inter(self):
        coefficient_obj = self.env["product.coefficient"]
        for template in self:
            template.coeff3_inter = coefficient_obj.compute_price(
                template.coeff3_id, template.coeff2_inter
            )
            if template.incl_in_standard_price_3:
                template.coeff3_inter_sp = coefficient_obj.compute_price(
                    template.coeff3_id, template.coeff2_inter_sp
                )
            else:
                template.coeff3_inter_sp = template.coeff2_inter_sp

    @api.depends(
        "coeff3_inter",
        "coeff4_id.operation_type",
        "coeff4_id.value",
        "incl_in_standard_price_4",
    )
    def _compute_coeff4_inter(self):
        coefficient_obj = self.env["product.coefficient"]
        for template in self:
            template.coeff4_inter = coefficient_obj.compute_price(
                template.coeff4_id, template.coeff3_inter
            )
            if template.incl_in_standard_price_4:
                template.coeff4_inter_sp = coefficient_obj.compute_price(
                    template.coeff4_id, template.coeff3_inter_sp
                )
            else:
                template.coeff4_inter_sp = template.coeff3_inter_sp

    @api.depends(
        "coeff4_inter",
        "coeff5_id.operation_type",
        "coeff5_id.value",
        "incl_in_standard_price_5",
    )
    def _compute_coeff5_inter(self):
        coefficient_obj = self.env["product.coefficient"]
        for template in self:
            template.coeff5_inter = coefficient_obj.compute_price(
                template.coeff5_id, template.coeff4_inter
            )
            if template.incl_in_standard_price_5:
                template.coeff5_inter_sp = coefficient_obj.compute_price(
                    template.coeff5_id, template.coeff4_inter_sp
                )
            else:
                template.coeff5_inter_sp = template.coeff4_inter_sp

    @api.depends(
        "coeff5_inter",
        "coeff6_id.operation_type",
        "coeff6_id.value",
        "incl_in_standard_price_6",
    )
    def _compute_coeff6_inter(self):
        coefficient_obj = self.env["product.coefficient"]
        for template in self:
            template.coeff6_inter = coefficient_obj.compute_price(
                template.coeff6_id, template.coeff5_inter
            )
            if template.incl_in_standard_price_6:
                template.coeff6_inter_sp = coefficient_obj.compute_price(
                    template.coeff6_id, template.coeff5_inter_sp
                )
            else:
                template.coeff6_inter_sp = template.coeff5_inter_sp

    @api.depends(
        "coeff6_inter",
        "coeff7_id.operation_type",
        "coeff7_id.value",
        "incl_in_standard_price_7",
    )
    def _compute_coeff7_inter(self):
        coefficient_obj = self.env["product.coefficient"]
        for template in self:
            template.coeff7_inter = coefficient_obj.compute_price(
                template.coeff7_id, template.coeff6_inter
            )
            if template.incl_in_standard_price_7:
                template.coeff7_inter_sp = coefficient_obj.compute_price(
                    template.coeff7_id, template.coeff6_inter_sp
                )
            else:
                template.coeff7_inter_sp = template.coeff6_inter_sp

    @api.depends(
        "coeff7_inter",
        "coeff8_id.operation_type",
        "coeff8_id.value",
        "incl_in_standard_price_8",
    )
    def _compute_coeff8_inter(self):
        coefficient_obj = self.env["product.coefficient"]
        for template in self:
            template.coeff8_inter = coefficient_obj.compute_price(
                template.coeff8_id, template.coeff7_inter
            )
            if template.incl_in_standard_price_8:
                template.coeff8_inter_sp = coefficient_obj.compute_price(
                    template.coeff8_id, template.coeff7_inter_sp
                )
            else:
                template.coeff8_inter_sp = template.coeff7_inter_sp

    @api.depends(
        "coeff8_inter",
        "coeff9_id.operation_type",
        "coeff9_id.value",
        "incl_in_standard_price_9",
    )
    def _compute_coeff9_inter(self):
        coefficient_obj = self.env["product.coefficient"]
        for template in self:
            template.coeff9_inter = coefficient_obj.compute_price(
                template.coeff9_id, template.coeff8_inter
            )
            if template.incl_in_standard_price_9:
                template.coeff9_inter_sp = coefficient_obj.compute_price(
                    template.coeff9_id, template.coeff8_inter_sp
                )
            else:
                template.coeff9_inter_sp = template.coeff8_inter_sp

    @api.depends(
        "coeff9_inter",
        "taxes_id.amount",
        "taxes_id.price_include",
        "taxes_id.price_include_override",
        "taxes_id.amount_type",
        "name",
    )
    def _compute_theoritical_price(self):
        for template in self:
            multi = 1
            theoritical_warning_label = ""
            for tax in template.taxes_id:
                if tax.amount_type == "percent" or tax.price_include:
                    multi *= 1 + (tax.amount / 100)
                if tax.amount_type != "percent" or not tax.price_include:
                    theoritical_warning_label = self.env._(
                        "Unimplemented Feature\n"
                        "The Tax %s is not correctly set for computing"
                        " prices with coefficients for the product %s",
                        tax.name,
                        template.name,
                    )
            template.theoritical_price = template.coeff9_inter * multi
            template.theoritical_warning_label = theoritical_warning_label

    @api.depends(
        "theoritical_price",
        "list_price",
        "base_price",
        "alternative_base_price_sale",
    )
    def _compute_has_theoritical_price_different(self):
        for template in self:
            if template.theoritical_price and (
                template.base_price or template.alternative_base_price_sale
            ):
                template.has_theoritical_price_different = float_round(
                    template.list_price, precision_digits=2
                ) != float_round(template.theoritical_price, precision_digits=2)
            else:
                template.has_theoritical_price_different = False

    @api.depends(
        "coeff9_inter_sp",
        "standard_price",
        "base_price",
        "alternative_base_price_standard",
    )
    def _compute_has_theoritical_cost_different(self):
        precision = self.env["decimal.precision"].precision_get("Product Sale Price")
        digits = precision or 2
        for template in self:
            if template.coeff9_inter_sp and (
                template.base_price or template.alternative_base_price_standard
            ):
                template.has_theoritical_cost_different = float_round(
                    template.standard_price, precision_digits=digits
                ) != float_round(template.coeff9_inter_sp, precision_digits=digits)
            else:
                template.has_theoritical_cost_different = False

    @api.model
    def _get_bool_param(self, key):
        return self.env["ir.config_parameter"].sudo().get_param(key) == "True"

    @api.model
    def get_auto_update_base_price(self):
        # Get Purchase Configuration: Updates Base Price automatically
        return self._get_bool_param("coop_product_coefficient.auto_update_base_price")

    @api.model
    def get_auto_update_theorical_cost(self):
        # Get Purchase Configuration: Updates Theorical Cost automatically
        return self._get_bool_param(
            "coop_product_coefficient.auto_update_theorical_cost"
        )

    @api.model
    def get_auto_update_theorical_price(self):
        # Get Purchase Configuration: Updates Theorical Price automatically
        return self._get_bool_param(
            "coop_product_coefficient.auto_update_theorical_price"
        )

    def auto_update_theoritical_cost_price(self):
        for obj in self:
            if obj.has_theoritical_cost_different and (
                obj.get_auto_update_theorical_cost()
            ):
                obj.use_theoritical_cost()
            if (
                obj.has_theoritical_price_different
                and obj.get_auto_update_theorical_price()
            ):
                obj.use_theoritical_price()

    def write(self, vals):
        ret = super().write(vals)
        if self._context.get("skip_price_update", False) is False:
            self.auto_update_theoritical_cost_price()
        return ret

    @api.model_create_multi
    def create(self, vals_list):
        new_objs = super().create(vals_list)
        new_objs.auto_update_theoritical_cost_price()
        return new_objs
