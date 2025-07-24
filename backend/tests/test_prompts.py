import unittest
from backend.apis.prompts import format_policy_prompt


class TestPromptGeneration(unittest.TestCase):
    def test_prompt_contains_user_details(self):
        user_profile = {
            "zip_code": "12345",
            "role": "veteran",
            "age": 45,
            "income_bracket": "low",
            "housing_status": "renter",
            "healthcare_access": "uninsured"
        }

        policy_text = "A new bill expands housing assistance for veterans in low-income communities."

        prompt = format_policy_prompt(user_profile, policy_text)

        # Assert that all the user context shows up in the prompt
        self.assertIn("12345", prompt)
        self.assertIn("veteran", prompt)
        self.assertIn("low", prompt)
        self.assertIn("renter", prompt)
        self.assertIn("uninsured", prompt)
        self.assertIn(policy_text, prompt)


if __name__ == "__main__":
    unittest.main()
