from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import uuid

from apis.congress_api import *
from apis.federal_register import *
from apis.genai import create_explainer, PolicyExplainError
from apis.geocodio_client import create_geocodio_client
from models import db

# Load .env from .venv if present
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.venv/.env"))

# App and CORS setup
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

# Create clients
explainer = create_explainer()
congress_client = create_congress_client()
fedreg_client = create_federal_register_client()
geocodio_client = create_geocodio_client()

@app.route("/api/ping", methods=["GET"])
def ping():
    return jsonify({"message": "pong"})

@app.route("/api/explain", methods=["POST"])
def explain_policy():
    try:
        data = request.get_json()
        profile = {
            "zip_code": data["zip_code"],
            "role": data["role"],
            "age": int(data["age"]),
            "income_bracket": data["income_bracket"],
            "housing_status": data["housing_status"],
            "healthcare_access": data["healthcare_access"]
        }
        choice = str(data["policy_choice"])
        

        def browse_policies_by_topic():
            return "This is a sample policy on education reform."

        def get_recent_rules():
            return "Recent rules include EPA carbon limits and USDA SNAP updates."

        def search_policies():
            return "Search result: broadband equity funding policy."

        def browse_congressional_bills():
            return "Example bill: H.R.1234 — Affordable Childcare for All Act."

        def search_congressional_bills():
            return "Result: S.456 — Cybersecurity for Critical Infrastructure Act."

        def get_trending_bills():
            return "Trending: H.R.7890 — National AI Standards Framework."

        def get_policy_text(choice):
            if choice == "1":
                return data.get("policy_text", "No policy provided")
            elif choice == "2":
                return browse_policies_by_topic()
            elif choice == "3":
                return get_recent_rules()
            elif choice == "4":
                return search_policies()
            elif choice == "5":
                return browse_congressional_bills()
            elif choice == "6":
                return search_congressional_bills()
            elif choice == "7":
                return get_trending_bills()
            else:
                return "No valid option selected"

        policy_text = get_policy_text(choice)
        if not policy_text:
            return jsonify({"error": "No policy text found"}), 400

        explanation = explainer.generate_explanation(policy_text, profile)

        return jsonify({
            "zip_code": profile["zip_code"],
            "role": profile["role"],
            "explanation": explanation
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/policies", methods=["POST"])
def get_policies():
    data = request.get_json()
    print("Received request:", data)

    zip_code = data.get("zip")
    role = data.get("role", "general")
    age = data.get("age")
    income = data.get("income_bracket")
    housing = data.get("housing_status")
    healthcare = data.get("healthcare_access")

    role_topic_map = {
        "student": "education",
        "parent": "education",
        "veteran": "veterans",
        "worker": "employment",
    }

    topic = role_topic_map.get(role.lower(), "general")
    print(f"Resolved topic for role '{role}': {topic}")

    try:
        congress_bills = congress_client.get_bills_by_topic(topic)[:3]
        fed_policies = fedreg_client.get_policy_by_topic(topic)[:3]

        formatted_bills = [
            {
                "title": bill.get("title", "No title"),
                "summary": congress_client.get_bill_status_summary(bill)
            }
            for bill in congress_bills
        ]

        formatted_fed = [
            {
                "title": doc.get("title", "No title"),
                "summary": doc.get("abstract", "No summary available")
            }
            for doc in fed_policies
        ]

        return jsonify({
            "zip": zip_code,
            "role": role,
            "policies": formatted_bills + formatted_fed
        })

    except Exception as e:
        print("❌ Error during policy fetch:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        session_id = data.get("session_id") or str(uuid.uuid4())
        user_message = data.get("message", "")
        user_context = data.get("context", {})

        if not user_message.strip():
            return jsonify({"error": "Empty message"}), 400

        chat_history = db.get_recent_chat_context(session_id)
        bot_response = explainer.generate_chat_response(
            user_message=user_message,
            user_context=user_context,
            chat_history=chat_history
        )

        db.save_chat_message(session_id, user_message, bot_response)

        return jsonify({
            "session_id": session_id,
            "response": bot_response
        })

    except PolicyExplainError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {e}"}), 500

@app.route("/api/representatives", methods=["POST"])
def get_representatives():
    data = request.get_json()
    print("📦 ZIP data received:", data)

    zip_code = data.get("zip")
    if not zip_code:
        return jsonify({"error": "ZIP code is required"}), 400

    try:
        reps = geocodio_client.get_representatives(zip_code)
        return jsonify({"representatives": reps})
    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/api/policyhub", methods=["GET"])
def policy_hub():
    try:
        zip_code = request.args.get("zip")
        print("📥 PolicyHub request for ZIP:", zip_code)

        # Example topic logic (could also use demographics later)
        topic = "general"

        # Get policies from both APIs
        congress_bills = congress_client.get_bills_by_topic(topic)[:5]
        fed_policies = fedreg_client.get_policy_by_topic(topic)[:5]  # ← FIXED LINE

        formatted_bills = [
            {
                "title": bill.get("title", "No title"),
                "summary": congress_client.get_bill_status_summary(bill)
            }
            for bill in congress_bills
        ]

        formatted_fed = [
            {
                "title": doc.get("title", "No title"),
                "summary": doc.get("abstract", "No summary available")
            }
            for doc in fed_policies
        ]

        return jsonify({
            "zip": zip_code,
            "policies": formatted_bills + formatted_fed
        })

    except Exception as e:
        print("❌ PolicyHub error:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("🚀 CivicBridge Flask API running on http://localhost:5050")
    app.run(debug=True, host="localhost", port=5050)
