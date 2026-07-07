import unittest
from types import SimpleNamespace

from app.services.evaluation import build_evaluation_summary


class EvaluationSummaryTests(unittest.TestCase):
    def test_demo_records_are_excluded_from_validation_metrics(self):
        events = [
            SimpleNamespace(id=1, source_name="safeaudit-local-demo"),
            SimpleNamespace(id=2, source_name="authorised-test-video.mp4"),
            SimpleNamespace(id=3, source_name="authorised-test-video.mp4"),
        ]
        reviews = [
            SimpleNamespace(event_id=1, verdict="confirmed_violation"),
            SimpleNamespace(event_id=2, verdict="confirmed_violation"),
            SimpleNamespace(event_id=3, verdict="false_alarm"),
        ]

        summary = build_evaluation_summary(events, reviews)

        self.assertEqual(summary["demo_events"], 1)
        self.assertEqual(summary["real_events"], 2)
        self.assertEqual(summary["reviewed_real_events"], 2)
        self.assertEqual(summary["confirmed_violations"], 1)
        self.assertEqual(summary["false_alarms"], 1)
        self.assertEqual(summary["precision"], 0.5)
        self.assertEqual(summary["review_rate"], 1.0)
        self.assertTrue(summary["ready_for_reporting"])

    def test_no_real_reviews_does_not_claim_precision(self):
        events = [SimpleNamespace(id=1, source_name="safeaudit-local-demo")]
        reviews = [SimpleNamespace(event_id=1, verdict="confirmed_violation")]

        summary = build_evaluation_summary(events, reviews)

        self.assertEqual(summary["real_events"], 0)
        self.assertEqual(summary["demo_events"], 1)
        self.assertIsNone(summary["precision"])
        self.assertEqual(summary["review_rate"], 0.0)
        self.assertFalse(summary["ready_for_reporting"])


if __name__ == "__main__":
    unittest.main()
