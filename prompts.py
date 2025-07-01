def format_policy_prompt(user_profile, policy_text):
    """
    Builds a context-rich prompt string using extended user profile data.
    """
    return f"""
You are a civic policy explainer helping everyday Americans understand how policies affect them.

User profile:
- ZIP code: {user_profile.get("zip_code")}
- Role: {user_profile.get("role")}
- Age: {user_profile.get("age")}
- Income bracket: {user_profile.get("income_bracket")}
- Housing status: {user_profile.get("housing_status")}
- Healthcare access: {user_profile.get("healthcare_access")}

Policy:
\"\"\"{policy_text}\"\"\"

Please explain how this policy might affect this person in clear, plain English (no legal jargon). Focus on practical, day-to-day impacts: money, rights, services, housing, healthcare, education, taxes, etc.

Limit your response to 4–6 sentences.
"""
