from odoo import api, models

FOODCOOP_ADMIN_SETTINGS_APPS = {"coop_membership"}


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    def _is_foodcoop_admin_without_base_admin(self):
        return not self.env.user.has_group(
            "base.group_system"
        ) and self.env.user.has_group("foodcoop_data_role.group_Foodcoop_Admin")

    def _get_view(self, view_id=None, view_type="form", **options):
        if view_type == "form" and self._is_foodcoop_admin_without_base_admin():
            arch, view = super(ResConfigSettings, self.sudo())._get_view(
                view_id=view_id, view_type=view_type, **options
            )
            for app in arch.xpath("//app"):
                if app.get("name") not in FOODCOOP_ADMIN_SETTINGS_APPS:
                    app.getparent().remove(app)
            return arch, view
        return super()._get_view(view_id=view_id, view_type=view_type, **options)

    def _get_allowed_settings_fields(self):
        # Field names visible in the Foodcoop Admin filtered arch
        arch, _ = self.sudo()._get_view(view_type="form")
        return set(arch.xpath("//field/@name"))

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self._is_foodcoop_admin_without_base_admin():
            allowed = self._get_allowed_settings_fields()
            tmp = self.sudo().new({})
            # Populate related company fields that are in the allowed view
            res.update(
                {
                    n: tmp[n]
                    for n in fields_list
                    if n not in res
                    and (f := self._fields.get(n))
                    and f.related
                    and n in allowed
                }
            )
            # Strip non-allowed related fields: ORM's _add_missing_default_values
            # calls default_get() for every field absent from create() vals, so if we
            # return e.g. account_price_include here, the ORM inverse writes it to
            # res.company and triggers @api.constrains('account_price_include').
            for n in list(res):
                f = self._fields.get(n)
                if f and f.related and n not in allowed:
                    del res[n]
        return res

    @api.model_create_multi
    def create(self, vals_list):
        if self._is_foodcoop_admin_without_base_admin():
            sudo = self.sudo()
            allowed = self._get_allowed_settings_fields()
            # Strip non-allowed related fields from client vals before create so
            # their ORM inverse (write-through to res.company) is never triggered.
            vals_list = [
                {
                    k: v
                    for k, v in vals.items()
                    if k in allowed or not (f := self._fields.get(k)) or not f.related
                }
                for vals in vals_list
            ]
            return super(ResConfigSettings, sudo).create(vals_list)
        return super().create(vals_list)

    def execute(self):
        if self._is_foodcoop_admin_without_base_admin():
            return super(ResConfigSettings, self.sudo()).execute()
        return super().execute()
