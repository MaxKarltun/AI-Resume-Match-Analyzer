import unittest

from resume_analysis import build_suggestions, get_health_status


class ResumeAnalysisTests(unittest.TestCase):
    def test_health_thresholds(self):
        for score, expected in [
            (0, "Needs Improvement"), (59, "Needs Improvement"),
            (60, "Fair"), (74, "Fair"), (75, "Good"), (89, "Good"),
            (90, "Excellent"), (100, "Excellent"),
        ]:
            with self.subTest(score=score):
                self.assertEqual(get_health_status(score)[0], expected)

    def test_missing_skills_generate_honest_recommendations(self):
        suggestions = build_suggestions(["AWS", "Airflow"], "Python and SQL")
        self.assertIn("AWS", suggestions[0])
        self.assertIn("If you have", suggestions[0])
        self.assertIn("Airflow", suggestions[1])
        self.assertIn("measurable business impact", suggestions[2])

    def test_dates_and_phone_numbers_do_not_count_as_impact(self):
        suggestions = build_suggestions([], "2024-2026. Phone: 555-123-4567.")
        self.assertTrue(any("measurable business impact" in s for s in suggestions))

    def test_existing_quantified_impact_is_not_reported_missing(self):
        for text in (
            "Reduced processing time by 30%.",
            "Processed 50000 records.",
            "Saved $5000 in monthly costs.",
        ):
            with self.subTest(text=text):
                suggestions = build_suggestions([], text)
                self.assertFalse(
                    any("Add measurable business impact" in s for s in suggestions)
                )
                self.assertTrue(any("All detected job skills" in s for s in suggestions))


if __name__ == "__main__":
    unittest.main()
