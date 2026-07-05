import unittest

from app.services.ppe_detector import Detection, missing_ppe_for_person


class MissingPPERulesTests(unittest.TestCase):
    def setUp(self):
        self.person = Detection("person", 0.95, 100, 100, 300, 500)

    def test_detects_no_missing_items_when_helmet_and_vest_are_associated(self):
        detections = [
            self.person,
            Detection("helmet", 0.90, 150, 95, 225, 180),
            Detection("vest", 0.88, 140, 210, 260, 390),
        ]
        self.assertEqual(missing_ppe_for_person(self.person, detections, ["helmet", "vest"]), [])

    def test_flags_missing_helmet(self):
        detections = [
            self.person,
            Detection("vest", 0.88, 140, 210, 260, 390),
        ]
        self.assertEqual(missing_ppe_for_person(self.person, detections, ["helmet", "vest"]), ["helmet"])

    def test_ignores_ppe_belonging_to_a_different_person(self):
        detections = [
            self.person,
            Detection("helmet", 0.90, 420, 95, 490, 180),
            Detection("vest", 0.88, 410, 210, 510, 390),
        ]
        self.assertEqual(
            missing_ppe_for_person(self.person, detections, ["helmet", "vest"]),
            ["helmet", "vest"],
        )


if __name__ == "__main__":
    unittest.main()
