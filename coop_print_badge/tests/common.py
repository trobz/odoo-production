import base64
import io

from PIL import Image

from odoo.tests import common


class CoopPrintBadgeTest(common.TransactionCase):
    """Base class for Coop Print Badge tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ResPartner = cls.env["res.partner"]
        cls.IrConfigParameter = cls.env["ir.config_parameter"]
        cls.IrModelFields = cls.env["ir.model.fields"]
        f_img = io.BytesIO()
        Image.new("RGB", (500, 500), "#FFFFFF").save(f_img, "PNG")
        f_img.seek(0)
        cls.f_img_b64 = base64.b64encode(f_img.read())
