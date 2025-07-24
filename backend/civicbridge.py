import sys
import db
from apis.genai import (
    create_explainer,
    PolicyExplainError
)
from apis.federal_register import (
    create_federal_register_client,
    FederalRegisterError,
)


def collect_user_input():
    """Collect user profile information and policy preference."""
    print("Welcome to CivicBridge: Understand How Policies Impact You\n")

    zip_code = input("Enter your ZIP code: ")
    role = input(
        "Enter your role (e.g., student, renter, small business owner): ")
    age = input("Enter your age: ")
    income_bracket = input(
        "Enter your income bracket (e.g., low, middle, high): ")
    housing_status = input(
        "Enter your housing status (e.g., renter, homeowner): ")
    healthcare_access = input(
        "Enter your healthcare access (e.g., insured, Medicaid, uninsured): ")

    # Policy input options
    print("\nPolicy Options:")
    print("1. Enter a specific policy title or summary")
    print("2. Browse policies by topic")
    print("3. Get recent government rules")
    print("4. Search for policies")

    choice = input("Choose an option (1-4): ").strip()

    user_profile = {
        "zip_code": zip_code,
        "role": role,
        "age": int(age),
        "income_bracket": income_bracket,
        "housing_status": housing_status,
        "healthcare_access": healthcare_access
    }

    return user_profile, choice


def browse_policies_by_topic():
    """Let user browse policies by predefined topics."""
    topics = {
        '1': 'healthcare',
        '2': 'housing',
        '3': 'education',
        '4': 'employment',
        '5': 'taxes',
        '6': 'environment',
        '7': 'transportation',
        '8': 'immigration',
        '9': 'social_security',
        '10': 'veterans'
    }

    print("\nAvailable Topics:")
    for key, topic in topics.items():
        print(f"{key}. {topic.replace('_', ' ').title()}")

    topic_choice = input("Select a topic (1-10): ").strip()
    selected_topic = topics.get(topic_choice)

    if not selected_topic:
        print("Invalid topic selection.")
        return None

    try:
        fr_client = create_federal_register_client()
        documents = fr_client.get_policy_by_topic(selected_topic)

        if not documents:
            print(f"No recent policies found for {selected_topic}.")
            return None

        print(f"\nRecent {selected_topic.replace('_', ' ').title()} Policies:")
        for i, doc in enumerate(documents[:5], 1):
            title = doc.get('title', 'Unknown Policy')[:80]
            date = doc.get('publication_date', 'Unknown date')
            print(f"{i}. [{date}] {title}...")

        doc_choice = input(
            f"Select a policy (1-{min(5, len(documents))}): "
        ).strip()

        if not doc_choice.isdigit() or not (
            1 <= int(doc_choice) <= min(5, len(documents))
        ):
            print("Invalid policy selection.")
            return None

        try:
            selected_doc = documents[int(doc_choice) - 1]
            return fr_client.format_document_for_explanation(selected_doc)
        except (ValueError, IndexError):
            print("Invalid policy selection.")
            return None

    except FederalRegisterError as e:
        print(f"Error fetching policies: {e}")
        return None


def get_user_context():
    return {
        "zip_code": "06516",
        "role": "student",
        "age": 19,
        "income_bracket": "low",
        "housing_status": "renter",
        "healthcare_access": "insured"
    }


def get_recent_rules():
    """Fetch and display recent government rules."""
    try:
        fr_client = create_federal_register_client()
        documents = fr_client.get_recent_rules(days_back=14)

        if not documents:
            print("No recent rules found.")
            return None

        print("\nRecent Government Rules:")
        for i, doc in enumerate(documents[:5], 1):
            title = doc.get('title', 'Unknown Rule')[:80]
            date = doc.get('publication_date', 'Unknown date')
            agency = ', '.join([a.get('name', '')
                               for a in doc.get('agencies', [])])
            print(f"{i}. [{date}] {title}... (Agency: {agency})")

        doc_choice = input("Select a rule (1-5): ").strip()
        try:
            selected_doc = documents[int(doc_choice) - 1]
            return fr_client.format_document_for_explanation(selected_doc)
        except (ValueError, IndexError):
            print("Invalid rule selection.")
            return None

    except FederalRegisterError as e:
        print(f"Error fetching recent rules: {e}")
        return None


def search_policies():
    """Search for policies using user-provided terms."""
    search_term = input(
        "Enter search terms (e.g., 'student loan', 'tax credit'): ").strip()

    if not search_term:
        print("No search terms provided.")
        return None

    try:
        fr_client = create_federal_register_client()
        documents = fr_client.search_documents(search_term, days_back=90)

        if not documents:
            print(f"No policies found for '{search_term}'.")
            return None

        print(f"\nPolicies matching '{search_term}':")
        for i, doc in enumerate(documents[:5], 1):
            title = doc.get('title', 'Unknown Policy')[:80]
            date = doc.get('publication_date', 'Unknown date')
            print(f"{i}. [{date}] {title}...")

        doc_choice = input("Select a policy (1-5): ").strip()
        try:
            selected_doc = documents[int(doc_choice) - 1]
            return fr_client.format_document_for_explanation(selected_doc)
        except (ValueError, IndexError):
            print("Invalid policy selection.")
            return None

    except FederalRegisterError as e:
        print(f"Error searching policies: {e}")
        return None


def get_policy_text(choice):
    """Get policy text based on user choice."""
    if choice == "1":
        # Manual entry
        return input("\nEnter a policy title or short summary: ")
    elif choice == "2":
        # Browse by topic
        return browse_policies_by_topic()
    elif choice == "3":
        # Recent rules
        return get_recent_rules()
    elif choice == "4":
        # Search
        return search_policies()
    else:
        print("Invalid choice. Using manual entry.")
        return input("\nEnter a policy title or short summary: ")


def display_history(limit=None):
    """Display policy explanation history."""
    print("\n--- Policy Summary History ---\n")
    rows = db.get_all_responses(limit=limit)
    for row in rows:
        zip_code, role, policy, explanation = row
        print(f"> [{zip_code} - {role}] | {policy[:100]}...")
        print(f"{explanation[:200]}...\n")


def highlight(msg):
    return f"\033[96m{msg}\033[0m"


print(highlight("Welcome to CivicBridge: Understand How Policies Impact You"))


def main():
    """Main application entry point."""
    db.create_tables()

    # History flag
    if "--history" in sys.argv:
        limit = None if "--all" in sys.argv else 5
        display_history(limit)
        return

    if "--explain" in sys.argv:
        try:
            idx = sys.argv.index("--explain")
            topic = sys.argv[idx + 1]
        except IndexError:
            print("⚠️  Please provide a topic after --explain")
            return

        user_profile = get_user_context()  # you can make this silent/default later
        explainer = create_explainer()
        fr_client = create_federal_register_client()
        docs = fr_client.get_policy_by_topic(topic)

        if not docs:
            print(f"No policies found for topic '{topic}'")
            return

        doc = docs[0]
        policy_text = fr_client.format_document_for_explanation(doc)
        summary = explainer.generate_explanation(policy_text, user_profile)

        print("\n📘 Explanation:\n")
        print(summary)
        return

    # Collect input
    user_profile, choice = collect_user_input()

    # Get policy text based on choice
    policy_text = get_policy_text(choice)

    if not policy_text:
        print("No policy selected. Exiting.")
        return

    # Save user to DB
    user_id = db.insert_user(
        zip_code=user_profile["zip_code"],
        role=user_profile["role"],
        age=user_profile["age"],
        income_bracket=user_profile["income_bracket"],
        housing_status=user_profile["housing_status"],
        healthcare_access=user_profile["healthcare_access"]
    )

    # Store policy text (truncated for DB)
    policy_title = policy_text[:100] + \
        "..." if len(policy_text) > 100 else policy_text
    query_id = db.insert_query(user_id, policy_title)

    # Generate policy explanation using AI
    print("\n Generating personalized explanation...")

    try:
        explainer = create_explainer()
        summary = explainer.generate_explanation(policy_text, user_profile)
    except PolicyExplainError as e:
        print("\n❌ Could not generate summary:")
        print(e)
        return

    # Save result
    db.insert_response(query_id, summary)

    # Output
    print("\n" + "="*60)
    print(" PERSONALIZED POLICY EXPLANATION")
    print("="*60)
    print(summary)
    print("="*60)

    print(f"\n Results saved to database. Use --history to view all explanations.")


if __name__ == "__main__":
    main()
