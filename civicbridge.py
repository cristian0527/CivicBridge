import sys
import db
from genai import create_explainer, PolicyExplainError

def collect_user_input():
    print("Welcome to CivicBridge: Understand How Policies Impact You\n")

    zip_code = input("Enter your ZIP code: ")
    occupation = input("Enter your role (e.g., student, renter, small business owner): ")
    age = input("Enter your age: ")
    income_bracket = input("Enter your income bracket (e.g., low, middle, high): ")
    housing_status = input("Enter your housing status (e.g., renter, homeowner): ")
    healthcare_access = input("Enter your healthcare access (e.g., insured, Medicaid, uninsured): ")

    policy_title = input("\nEnter a policy title or short summary: ")

    user_profile = {
        "zip_code": zip_code,
        "occupation": occupation,
        "age": int(age),
        "income_bracket": income_bracket,
        "housing_status": housing_status,
        "healthcare_access": healthcare_access
    }

    return user_profile, policy_title

def display_history():
    print("\n--- Policy Summary History ---\n")
    rows = db.get_all_responses()
    for row in rows:
        zip_code, role, policy, explanation = row
        print(f"> [{zip_code} - {role}] | {policy}\n{explanation}\n")

def main():
    db.create_tables()

    # History flag
    if len(sys.argv) > 1 and sys.argv[1] == "--history":
        display_history()
        return

    # Collect input
    user_profile, policy_text = collect_user_input()

    # Save user to DB
    user_id = db.insert_user(
        zip_code=user_profile["zip_code"],
        role=user_profile["occupation"],  # stored as 'role' in DB
        age=user_profile["age"],
        income_bracket=user_profile["income_bracket"],
        housing_status=user_profile["housing_status"],
        healthcare_access=user_profile["healthcare_access"]
    )

    query_id = db.insert_query(user_id, policy_text)

    # Generate policy explanation using real AI
    explainer = create_explainer()
    try:
        summary = explainer.generate_explanation(policy_text, user_profile)
    except PolicyExplainError as e:
        print("\n❌ Could not generate summary:")
        print(e)
        return

    # Save result
    db.insert_response(query_id, summary)

    # Output
    print("\n--- Personalized Policy Summary ---\n")
    print(summary)

if __name__ == "__main__":
    main()
