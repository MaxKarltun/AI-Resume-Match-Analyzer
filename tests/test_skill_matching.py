import json
from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


class SkillMatchingTests(unittest.TestCase):
    def test_dashboard_charts_health_and_suggestions(self):
        app = AppTest.from_file(str(APP_PATH)).run()
        app.text_area[0].set_value("Python SQL Excel")
        app.text_area[1].set_value("Python SQL AWS Airflow")
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual(
            [metric.value for metric in app.metric], ["50%", "2", "2"]
        )
        charts = app.get("plotly_chart")
        self.assertEqual(len(charts), 2)
        gauge = json.loads(charts[0].proto.spec)["data"][0]
        bars = json.loads(charts[1].proto.spec)["data"][0]
        self.assertEqual(gauge["value"], 50)
        self.assertEqual(bars["x"], ["Matched Skills", "Missing Skills"])
        self.assertEqual(bars["y"], [2, 2])
        rendered = "\n".join(item.value for item in app.markdown)
        self.assertIn("Needs Improvement", rendered)
        self.assertIn("If you have AWS experience", rendered)
        self.assertIn("measurable business impact", rendered)

    def test_title_variants_and_document_formatting(self):
        app = AppTest.from_file(str(APP_PATH)).run()
        for resume in (
            "Data Engineer, SQL, ETL",
            "Data Engineers, sql, etl",
            "Data\nEngineering, S\u200bQL, ETL",
            "Data\u00a0 Engineer, \uff33\uff31\uff2c, ETL",
        ):
            with self.subTest(resume=resume):
                app.text_area[0].set_value(resume)
                app.text_area[1].set_value("Data Engineering, SQL, ETL")
                app.button[0].click().run()
                self.assertFalse(app.exception)
                self.assertEqual(
                    [metric.value for metric in app.metric],
                    ["100%", "3", "0"],
                )

    def test_aliases_do_not_double_count_skills(self):
        app = AppTest.from_file(str(APP_PATH)).run()
        app.text_area[0].set_value("Data Engineer, Data Engineering, ETL")
        app.text_area[1].set_value("Data Engineering, Data Engineers, SQL, ETL")
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual(
            [metric.value for metric in app.metric], ["67%", "2", "1"]
        )

    def test_sql_in_resume_is_not_a_match_unless_in_job(self):
        app = AppTest.from_file(str(APP_PATH)).run()
        app.text_area[0].set_value("SQL ETL")
        app.text_area[1].set_value("ETL Python")
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual(
            [metric.value for metric in app.metric], ["50%", "1", "1"]
        )
        details = app.expander[0]
        self.assertIn("ETL, SQL", details.markdown[0].value)
        self.assertIn("ETL, Python", details.markdown[1].value)

    def test_sql_does_not_match_inside_mysql(self):
        app = AppTest.from_file(str(APP_PATH)).run()
        app.text_area[0].set_value("MySQL")
        app.text_area[1].set_value("SQL")
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "0%")


if __name__ == "__main__":
    unittest.main()
