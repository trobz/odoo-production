from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestL10nFrCoopDefaultPricetag(TransactionCase):
    """Tests for 'l10n FR Coop Default Pricetag' Module"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id |= cls.env.ref(
            "coop_default_pricetag.group_food_manager"
        )
        cls.Country = cls.env["res.country"]
        cls.Department = cls.env["res.country.department"]
        cls.country_fr = cls.env.ref("base.fr")
        cls.department_paris = cls.env.ref(
            "l10n_fr_department.res_country_department_paris"
        )
        cls.department_seine = cls.env.ref(
            "l10n_fr_department.res_country_department_seinesaintdenis"
        )

    @classmethod
    def _create_prod_tmpl_form(self, department=None, country=None):
        form = Form(self.env["product.template"].with_user(self.env.user))
        form.name = "Test Product"
        if country:
            form.country_id = country
        if department:
            form.department_id = department
        return form

    def test_01_onchange_department_sets_country(self):
        """Test that selecting department automatically sets the country"""
        form = self._create_prod_tmpl_form(department=self.department_paris)
        record = form.save()
        self.assertRecordValues(
            record,
            [
                {
                    "department_id": self.department_paris.id,
                    "country_id": self.country_fr.id,
                }
            ],
        )

    def test_02_onchange_department_clears_country(self):
        """Test that clearing department clears the country"""
        form = self._create_prod_tmpl_form(country=self.country_fr)
        form.department_id = self.Department
        record = form.save()
        self.assertRecordValues(
            record,
            [
                {
                    "department_id": False,
                    "country_id": False,
                }
            ],
        )

    def test_03_onchange_country_clears_department(self):
        """Test that changing country clears the department"""
        country_us = self.env.ref("base.us")
        form = self._create_prod_tmpl_form(
            department=self.department_paris, country=self.country_fr
        )
        form.country_id = country_us
        record = form.save()
        self.assertRecordValues(
            record,
            [
                {
                    "department_id": False,
                    "country_id": False,
                }
            ],
        )

    def test_04_compute_pricetag_origin_with_country(self):
        """Test pricetag_origin computation with country only"""
        form = self._create_prod_tmpl_form(country=self.country_fr)
        form.origin_description = "Local product"
        record = form.save()
        self.assertRecordValues(
            record,
            [
                {
                    "pricetag_origin": "FRANCE - Local product",
                }
            ],
        )

    def test_05_compute_pricetag_origin_with_department(self):
        """Test pricetag_origin computation with department"""
        form = self._create_prod_tmpl_form(department=self.department_paris)
        form.origin_description = "Organic"
        record = form.save()
        self.assertIn(
            "Paris",
            record.pricetag_origin,
            "Pricetag origin should contain department name in uppercase",
        )
        self.assertIn(
            "FRANCE",
            record.pricetag_origin,
            "Pricetag origin should contain country name in uppercase",
        )

    def test_06_compute_pricetag_origin_with_maker(self):
        """Test pricetag_origin computation with maker description"""
        form = self._create_prod_tmpl_form(country=self.country_fr)
        form.maker_description = "Test Maker"
        record = form.save()
        self.assertIn(
            "Test Maker",
            record.pricetag_origin,
            "Pricetag origin should contain maker description",
        )

    def test_07_compute_pricetag_origin_all_fields(self):
        """Test pricetag_origin computation with all fields"""
        form = self._create_prod_tmpl_form(
            department=self.department_paris, country=self.country_fr
        )
        form.origin_description = "Local farm"
        form.maker_description = "Farmer John"
        record = form.save()
        self.assertIn("FRANCE", record.pricetag_origin)
        self.assertIn("Paris", record.pricetag_origin)
        self.assertIn("Local farm", record.pricetag_origin)
        self.assertIn("Farmer John", record.pricetag_origin)
