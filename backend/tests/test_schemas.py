import unittest

from pydantic import ValidationError

from app.schemas import ZoneCreate


class ZoneSchemaTests(unittest.TestCase):
    def test_zone_normalises_name_and_supported_ppe(self):
        zone = ZoneCreate(
            name="  Assembly   Bay  ",
            required_ppe=["Helmet", "vest", "helmet"],
            coordinates=[80, 80, 500, 430],
        )

        self.assertEqual(zone.name, "Assembly Bay")
        self.assertEqual(zone.required_ppe, ["helmet", "vest"])

    def test_zone_rejects_zero_area_rectangle(self):
        with self.assertRaises(ValidationError):
            ZoneCreate(name="Assembly Bay", required_ppe=["helmet"], coordinates=[80, 80, 80, 430])

    def test_zone_rejects_reversed_rectangle(self):
        with self.assertRaises(ValidationError):
            ZoneCreate(name="Assembly Bay", required_ppe=["helmet"], coordinates=[500, 430, 80, 80])

    def test_zone_rejects_negative_coordinates(self):
        with self.assertRaises(ValidationError):
            ZoneCreate(name="Assembly Bay", required_ppe=["helmet"], coordinates=[-1, 80, 500, 430])

    def test_zone_rejects_unsupported_ppe(self):
        with self.assertRaises(ValidationError):
            ZoneCreate(name="Assembly Bay", required_ppe=["gloves"], coordinates=[80, 80, 500, 430])

    def test_zone_rejects_whitespace_only_name(self):
        with self.assertRaises(ValidationError):
            ZoneCreate(name="   ", required_ppe=["helmet"], coordinates=[80, 80, 500, 430])


if __name__ == "__main__":
    unittest.main()
