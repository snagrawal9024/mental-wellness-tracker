import unittest
import datetime
import pandas as pd
from mindmate_tool import detect_crisis, generate_suggestions, create_check_in, generate_report, CheckIn


class TestMindMateTool(unittest.TestCase):
    def test_detect_crisis(self):
        self.assertTrue(detect_crisis("I want to kill myself"))
        self.assertTrue(detect_crisis("Sometimes I want to disappear."))
        self.assertFalse(detect_crisis("I feel good today."))

    def test_generate_suggestions_stress_and_sleep(self):
        check = CheckIn(date=datetime.date.today(), name="Test", exam="JEE", mood="Anxious",
                        stress=9, sleep_hours=5.0, study_hours=4.0, triggers=[], journal="test journal")
        suggestions = generate_suggestions(check)
        self.assertTrue(any("six hours" in s.lower() for s in suggestions))

    def test_generate_suggestions_mock_test(self):
        check = CheckIn(date=datetime.date.today(), name="Test", exam="JEE", mood="Calm",
                        stress=3, sleep_hours=7.0, study_hours=4.0, triggers=["Mock test"], journal="test")
        suggestions = generate_suggestions(check)
        self.assertTrue(any("mock test" in s.lower() for s in suggestions))

    def test_generate_suggestions_parental(self):
        check = CheckIn(date=datetime.date.today(), name="Test", exam="JEE", mood="Calm",
                        stress=4, sleep_hours=7.0, study_hours=4.0, triggers=["Parental pressure"], journal="test")
        suggestions = generate_suggestions(check)
        self.assertTrue(any("parental" in s.lower() for s in suggestions))

    def test_generate_suggestions_comparison(self):
        check = CheckIn(date=datetime.date.today(), name="Test", exam="JEE", mood="Calm",
                        stress=4, sleep_hours=7.0, study_hours=4.0, triggers=["Comparison with peers"], journal="test")
        suggestions = generate_suggestions(check)
        self.assertTrue(any("comparison" in s.lower() for s in suggestions))

    def test_generate_suggestions_breathing(self):
        check = CheckIn(date=datetime.date.today(), name="Test", exam="JEE", mood="Tired",
                        stress=6, sleep_hours=8.0, study_hours=4.0, triggers=[], journal="test")
        suggestions = generate_suggestions(check)
        self.assertTrue(any("breathing" in s.lower() for s in suggestions))

    def test_generate_suggestions_journal_length(self):
        check = CheckIn(date=datetime.date.today(), name="Test", exam="JEE", mood="Calm",
                        stress=2, sleep_hours=8.0, study_hours=4.0, triggers=[], journal="short")
        suggestions = generate_suggestions(check)
        self.assertTrue(any("journal" in s.lower() or "journaling" in s.lower() for s in suggestions))

    def test_create_check_in_store_false(self):
        date = datetime.date(2024, 1, 1)
        check, suggestions, crisis = create_check_in(
            name="Test", exam="JEE", mood="Happy", stress=4,
            sleep_hours=8.0, study_hours=4.0, triggers=[],
            journal="no crisis", date=date, store=False
        )
        self.assertIsInstance(check, CheckIn)
        self.assertFalse(crisis)
        self.assertEqual(check.date, date)

    def test_generate_report(self):
        data = {
            'date': ['2024-01-01', '2024-01-02'],
            'name': ['A', 'B'],
            'exam': ['JEE', 'NEET'],
            'mood': ['Happy', 'Sad'],
            'stress': [5, 3],
            'sleep_hours': [7.0, 8.0],
            'study_hours': [6.0, 7.0],
            'triggers': ['', ''],
            'journal': ['', ''],
        }
        df = pd.DataFrame(data)
        summary, figs = generate_report(df)
        self.assertIn("Total check‑ins: 2", summary)
        self.assertEqual(len(figs), 3)


if __name__ == '__main__':
    unittest.main()
