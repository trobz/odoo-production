from .common import CoopPrintBadgeTest


class TestResPartner(CoopPrintBadgeTest):
    """Test res.partner badge functionality."""

    def test_get_badge_image(self):
        """Test get_badge_image returns properly sized image."""
        result = self.ResPartner.get_badge_image(self.f_img_b64)
        self.assertTrue(result)

    def test_untick_badges_to_print(self):
        """Test untick_badges_to_print sets badge_to_print to False."""
        partner = self.ResPartner.create(
            {
                "name": "Test Partner",
                "badge_to_print": True,
            }
        )
        self.assertTrue(partner.badge_to_print)
        partner.untick_badges_to_print()
        self.assertFalse(partner.badge_to_print)

    def test_check_badge_to_print_no_trigger_fields(self):
        """Test _check_badge_to_print with no trigger fields."""
        partner = self.ResPartner.create(
            {
                "name": "Test Partner",
            }
        )
        result = partner._check_badge_to_print({})
        self.assertFalse(result)

    def test_create_sets_image_badge(self):
        """Test create sets image_badge when image_1920 provided."""
        partner = self.ResPartner.create(
            {
                "name": "Test Partner With Image",
                "image_1920": self.f_img_b64,
            }
        )
        self.assertTrue(partner.image_badge)

    def test_write_sets_badge_to_print_on_trigger_field_change(self):
        """Test write sets badge_to_print when trigger field changes."""
        field = self.IrModelFields.search(
            [("model", "=", "res.partner"), ("name", "=", "name")], limit=1
        )
        if field:
            company = self.env.company
            company.reprint_change_field_ids = [(6, 0, [field.id])]
            partner = self.ResPartner.create(
                {
                    "name": "Test Partner",
                    "badge_to_print": False,
                }
            )
            partner.write({"name": "New Name"})
            self.assertTrue(partner.badge_to_print)
