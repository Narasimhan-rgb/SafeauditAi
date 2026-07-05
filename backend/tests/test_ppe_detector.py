import unittest

from app.services.ppe_detector import Detection, missing_ppe_for_person


class PpeAssociationTests(unittest.TestCase):
    def setUp(self):
        self.person = Detection(
            label="person",
            confidence=0.98,
            x1=100,
            y1=100,
            x2=300,
            y2=500,
        )

    def test_worker_with_helmet_and_vest_is_compliant(self):
        detections = [
            self.person,
            Detection("helmet", 0.92, 155, 105, 230, 175),
            Detection("vest", 0.89, 145, 220, 260, 390),
        ]
        self.assertEqual(
            missing_ppe_for_person(self.person, detections, ["helmet", "vest"]),
            [],
        )

    def test_missing_helmet_is_reported(self):
        detections = [
            self.person,
            Detection("vest", 0.89, 145, 220, 260, 390),
        ]
        self.assertEqual(
            missing_ppe_for_person(self.person, detections, ["helmet", "vest"]),
            ["helmet"],
        )

    def test_other_workers_ppe_is_not_reused(self):
        detections = [
            self.person,
            Detection("helmet", 0.95, 410, 100, 485, 175),
            Detection("vest", 0.95, 410, 220, 500, 390),
        ]
        self.assertEqual(
            missing_ppe_for_person(self.person, detections, ["helmet", "vest"]),
            ["helmet", "vest"],
        )


if __name__ == "__main__":
    unittest.main()
