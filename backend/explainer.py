import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold  
from dotenv import load_dotenv
import os
import traceback

load_dotenv()

API_KEY = os.getenv("GOOGLE_GENAI_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_GENAI_API_KEY not found in .env")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-pro")


class PolicyExplainError(Exception):
    pass


class Explainer:
    def generate_chat_response(self, user_message, user_context, chat_history):
        zip_code = user_context.get("zip", "00000")
        role = user_context.get("role", "general")
        return f"This is a sample explanation for ZIP {zip_code} and role {role}. Message: {user_message}"

    def generate_explanation(self, policy_text, profile):
        prompt = self.build_prompt(policy_text, profile)
        print("📝 Prompt sent to Gemini:\n", prompt)

        try:
            response = model.generate_content(prompt)
            print("✅ Gemini response received.")
            print("🔍 Response text:", response.text)
            return response.text.strip()
        except Exception as e:
            print("❌ Gemini Error:", e)
            traceback.print_exc()
            raise PolicyExplainError(f"Gemini failed: {e}")

    def build_prompt(self, policy_text, profile):
        return f"""
You are a policy explainer. Break down the following policy in plain, human language.

Audience Profile:
- Role: {profile.get("role")}
- ZIP Code: {profile.get("zip_code")}
- Age: {profile.get("age")}
- Income Bracket: {profile.get("income_bracket")}
- Housing Status: {profile.get("housing_status")}
- Healthcare Access: {profile.get("healthcare_access")}

Policy Summary:
{policy_text}

Explain how this policy is likely to impact someone like the user above.
Use simple terms and avoid legal jargon.
"""

def create_explainer():
    return Explainer()
