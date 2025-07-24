"""
Google GenAI integration for CivicBridge policy explanations.

This module handles the AI-powered generation of personalized, plain-English
explanations of government policies based on user context.
"""

import os
import logging
from typing import Optional, Dict, Any
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv

load_dotenv()


class PolicyExplainError(Exception):
    """Custom exception for policy explanation errors."""


class PolicyExplainer:
    """Handles AI-powered policy explanations using Google GenAI."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GOOGLE_GENAI_API_KEY')
        if not self.api_key:
            raise PolicyExplainError(
                "Google GenAI API key required. Set GOOGLE_GENAI_API_KEY "
                "environment variable or pass api_key parameter."
            )

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.logger = logging.getLogger(__name__)

    def generate_explanation(
        self,
        policy_text: str,
        user_context: Dict[str, Any],
        max_tokens: int = 500
    ) -> str:
        try:
            prompt = self._build_prompt(policy_text, user_context)

            safety_settings = {
                HarmCategory.HARM_CATEGORY_HATE_SPEECH:
                    HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT:
                    HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT:
                    HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HARASSMENT:
                    HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }

            response = self.model.generate_content(
                prompt,
                safety_settings=safety_settings,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.3,
                )
            )

            if not response.text:
                raise PolicyExplainError("Empty response from GenAI API")

            self.logger.info("Successfully generated policy explanation")
            return response.text.strip()

        except Exception as original_error:
            error_msg = f"Failed to generate policy explanation: {str(original_error)}"
            self.logger.error(
                "Error generating explanation: %s", str(original_error))
            raise PolicyExplainError(error_msg) from original_error

    def _build_prompt(self, policy_text: str, user_context: Dict[str, Any]) -> str:
        zip_code = user_context.get("zip_code", "N/A")
        role = user_context.get("role", "general citizen")
        age = user_context.get("age", "N/A")
        income = user_context.get("income_bracket", "N/A")
        housing = user_context.get("housing_status", "N/A")
        healthcare = user_context.get("healthcare_access", "N/A")

        missing_fields = [
            k for k in ["zip_code", "role", "age", "income_bracket", "housing_status", "healthcare_access"]
            if not user_context.get(k)
        ]
        if missing_fields:
            self.logger.warning(
                f"Missing user context fields: {missing_fields}")

        prompt = f"""
You are CivicBridge, an AI assistant that explains government policies in simple,
personalized terms. Your goal is to help citizens understand how policies affect them directly.

USER CONTEXT:
- Zip Code: {zip_code}
- Role: {role}
- Age: {age}
- Income Bracket: {income}
- Housing Status: {housing}
- Healthcare Access: {healthcare}

POLICY TO EXPLAIN:
{policy_text}

INSTRUCTIONS:
1. Explain this policy in plain English (8th-grade reading level)
2. Focus specifically on how it affects someone in the user's situation
3. Be factual and non-partisan
4. Include practical implications (costs, benefits, requirements, deadlines)
5. If the policy doesn't directly affect this user, explain why
6. Keep the explanation under 400 words
7. Use bullet points for key impacts when helpful

RESPONSE FORMAT:
Start with a one-sentence summary, then provide details about personal impact.

Example structure:
"This policy [brief summary of what it does].

For someone in your situation:
• [Direct impact 1]
• [Direct impact 2]
• [What you need to know/do]

[Additional context if needed]"

Generate a clear, helpful explanation now:
"""
        return prompt

    def validate_policy_text(self, policy_text: str) -> bool:
        if not policy_text or not policy_text.strip():
            return False
        if len(policy_text.strip()) < 10:
            return False
        if len(policy_text) > 10000:
            self.logger.warning("Policy text truncated due to length")
            return True
        return True

    def get_sample_explanation(self) -> str:
        sample_policy_text = (
            "The Inflation Reduction Act includes provisions for clean energy tax credits, "
            "allowing homeowners to claim up to $7,500 for electric vehicle purchases and "
            "30% tax credits for solar panel installations through 2032."
        )

        sample_context = {
            'zip_code': '90210',
            'role': 'teacher',
            'age': 35,
            'income_bracket': 'middle',
            'housing_status': 'renter',
            'healthcare_access': 'private'
        }

        return self.generate_explanation(sample_policy_text, sample_context)


def create_explainer(api_key: Optional[str] = None) -> PolicyExplainer:
    return PolicyExplainer(api_key)


if __name__ == "__main__":
    import json

    logging.basicConfig(level=logging.INFO)

    try:
        explainer = create_explainer()

        SAMPLE_POLICY = (
            "The CHIPS and Science Act provides $52 billion in subsidies for domestic "
            "semiconductor manufacturing and research, aimed at reducing dependence on "
            "foreign chip production and strengthening U.S. technological competitiveness."
        )

        SAMPLE_USER = {
            'zip_code': '02101',
            'role': 'software engineer'
        }

        print("Testing CivicBridge Policy Explainer...")
        print("=" * 50)
        print(f"Policy: {SAMPLE_POLICY}")
        print(f"User: {json.dumps(SAMPLE_USER, indent=2)}")
        print("=" * 50)

        EXPLANATION = explainer.generate_explanation(
            SAMPLE_POLICY, SAMPLE_USER)
        print("EXPLANATION:")
        print(EXPLANATION)

    except PolicyExplainError as error:
        print(f"Policy explanation error: {error}")
        print("\nMake sure to set your GOOGLE_GENAI_API_KEY environment variable!")
    except (KeyError, ValueError, TypeError) as error:
        print(f"Configuration error: {error}")
    except ImportError as error:
        print(f"Import error: {error}")
        print("Make sure google-generativeai is installed: pip install google-generativeai")
