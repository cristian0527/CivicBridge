import unittest
from genai import create_explainer


class TestGenAI(unittest.TestCase):
    def test_generate_summary_returns_string(self):
        explainer = create_explainer()

        user_profile = {
            "zip_code": "11206",
            "occupation": "teacher",
            "age": 28,
            "income_bracket": "low",
            "housing_status": "renter",
            "healthcare_access": "Medicaid"
        }

        policy_text = (
            "This executive order expands access to school meal programs in underserved communities."
        )

        summary = explainer.generate_explanation(policy_text, user_profile)
        self.assertIsInstance(summary, str)
        self.assertTrue(len(summary) > 10)


if __name__ == "__main__":
    unittest.main()
