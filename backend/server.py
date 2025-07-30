from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import uuid

from apis.congress_api import *
from apis.federal_register import *
from apis.genai import create_explainer, PolicyExplainError
from apis.geocodio_client import create_geocodio_client
from explainer import PolicyExplainError
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
            "immigration_status": data["immigration_status"],
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

        bot_response = explainer.generate_enhanced_chat_response(
            user_message=user_message,
            user_context=user_context,
            chat_history=chat_history,
            congress_client=congress_client,
            geocodio_client=geocodio_client
        )

        db.save_chat_message(session_id, user_message, bot_response)

        return jsonify({
            "session_id": session_id,
            "response": bot_response
        })

    except PolicyExplainError as e:
        fallback_response = f"I'm currently experiencing high demand. Here's what I can tell you: {user_message[:100]}... Please try again in a moment for a detailed explanation."
        db.save_chat_message(session_id, user_message, fallback_response)
        return jsonify({
            "session_id": session_id,
            "response": fallback_response,
            "source": "fallback",
            "error": str(e)
            }), 500
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


@app.route("/api/representative/<bioguide_id>", methods=["GET"])
def get_representative_details(bioguide_id):
    """Get detailed information about a specific representative's legislative activity"""
    try:
        print(f"📋 Getting details for representative: {bioguide_id}")
        
        # Get member details from Congress API
        member_details = congress_client.get_member_details(bioguide_id)

        # Defensive unpacking of possibly weird structures
        depiction = member_details.get('depiction')
        if not isinstance(depiction, dict):
            depiction = {}

        current_member = member_details.get('currentMember')
        if not isinstance(current_member, dict):
            current_member = {}

        # Get legislative activity (combines sponsored + cosponsored bills)
        legislative_activity = congress_client.get_member_voting_record(bioguide_id, limit=15)

        response_data = {
            'representative': {
                "bioguide_id": bioguide_id,
                "name": f"{member_details.get('firstName', '')} {member_details.get('lastName', '')}".strip(),
                "party": member_details.get('partyName', ''),
                "state": member_details.get('state', ''),
                "district": member_details.get('district'),
                "office_url": member_details.get('officialWebsiteUrl', ''),
                "photo_url": depiction.get('imageUrl', ''),
                "chamber": current_member.get('chamber', '')
            },
            "legislative_activity": legislative_activity,
            "summary": {
                "total_items": len(legislative_activity),
                "sponsored_count": len([item for item in legislative_activity if item.get('position') == 'Sponsored']),
                "cosponsored_count": len([item for item in legislative_activity if item.get('position') == 'Cosponsored'])
            }
        }

        print(f"✅ Successfully retrieved {len(legislative_activity)} items for {bioguide_id}")
        return jsonify(response_data)

    except Exception as e:
        print(f"❌ Error getting representative details for {bioguide_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/policyhub", methods=["POST"])  # Changed from GET to POST
def get_policyhub():
    data = request.get_json()
    topic = data.get("topic", "")
    print("📥 PolicyHub request for topic:", topic)
    
    # Valid topics 
    valid_topics = [
        'healthcare', 'housing', 'education', 'employment', 
        'taxes', 'environment', 'transportation', 'immigration',
        'social_security', 'veterans'
    ]
    
    if not topic or topic not in valid_topics:
        return jsonify({"error": f"Invalid topic. Must be one of: {valid_topics}"}), 400

    try:
        # Use existing federal register client to get policies by topic
        federal_policies = fedreg_client.get_policy_by_topic(topic)[:30]
        print(f"✅ Found {len(federal_policies)} federal policies for topic: {topic}")
        
        # Also get some Congress bills for this topic
        congress_bills = congress_client.get_bills_by_topic(topic, limit=30)
        print(f"✅ Found {len(congress_bills)} congress bills for topic: {topic}")
        congress_bills = [
            b for b in congress_bills 
            if topic.lower() in b.get("title", "").lower()
                or topic.lower() in b.get("summary", "").lower()
            ]
        # Format federal policies
        formatted_federal = []
        for p in federal_policies:
            formatted_federal.append({
                "title": p.get("title", "No title"),
                "summary": p.get("abstract", "No summary available")[:200] + "..." if p.get("abstract") else "No summary available",
                "date": p.get("publication_date", ""),
                "agency": ', '.join([a.get('name', '') for a in p.get('agencies', [])]),
                "type": p.get("type", "Rule"),
                "url": p.get("html_url", ""),
                "source": "Federal Register"
            })
        
        # Format congress bills  
        formatted_congress = []
        for p in congress_bills:
            formatted_congress.append({
                "title": p.get("title", "No title"),
                "summary": congress_client.get_bill_status_summary(p),
                "date": p.get("updateDate", ""),
                "agency": "U.S. Congress",
                "type": f"{p.get('type', '').upper()} {p.get('number', '')}",
                "url": p.get("url", ""),
                "source": "Congress"
            })

        # Combine both sources
        all_policies = formatted_federal + formatted_congress
        
        # Sort by date if possible (most recent first)
        try:
            all_policies.sort(key=lambda x: x.get('date', ''), reverse=True)
        except:
            pass  # If sorting fails, return unsorted

        return jsonify({
            "policies": all_policies,
            "topic": topic,
            "topic_display": topic.replace('_', ' ').title(),
            "total_count": len(all_policies),
            "federal_count": len(formatted_federal),
            "congress_count": len(formatted_congress)
        })
        
    except Exception as e:
        print("❌ PolicyHub error:", e)
        return jsonify({"error": str(e)}), 500

#@app.route("/api/policy-categories", methods=["GET"])
#def get_policy_categories():
    #"""Get available policy categories for the dropdown"""
    #categories = [
        #{"value": "healthcare", "label": "Healthcare"},
        #{"value": "housing", "label": "Housing"}, 
        #{"value": "education", "label": "Education"},
        #{"value": "employment", "label": "Employment"},
        #{"value": "taxes", "label": "Taxes"},
        #{"value": "environment", "label": "Environment"},
        #{"value": "transportation", "label": "Transportation"},
        #{"value": "immigration", "label": "Immigration"},
        #{"value": "social_security", "label": "Social Security"},
        #{"value": "veterans", "label": "Veterans"}
    #]
    
    #return jsonify({"categories": categories})

@app.route("/api/policies/search", methods=["POST"])
def search_policies():
    """Search for policies by keyword/query"""
    data = request.get_json()
    query = data.get("query", "").strip()
    
    if not query:
        return jsonify({"error": "Search query required"}), 400
    
    if len(query) < 2:
        return jsonify({"error": "Search query must be at least 2 characters"}), 400
    
    try:
        print(f"📥 Policy search request for: {query}")
        
        # Search federal register with the query
        results = fedreg_client.search_documents(query, per_page=15)
        
        # Also search congress bills 
        congress_results = congress_client.search_bills(query, limit=10)
        
        # Format federal register results
        formatted_federal = []
        for doc in results:
            formatted_federal.append({
                "title": doc.get("title", "No title"),
                "summary": doc.get("abstract", "No summary available")[:200] + "..." if doc.get("abstract") else "No summary available",
                "date": doc.get("publication_date", ""),
                "agency": ', '.join([a.get('name', '') for a in doc.get('agencies', [])]),
                "type": doc.get("type", "Rule"),
                "url": doc.get("html_url", ""),
                "source": "Federal Register"
            })
        
        # Format congress results
        formatted_congress = []
        for bill in congress_results:
            formatted_congress.append({
                "title": bill.get("title", "No title"),
                "summary": congress_client.get_bill_status_summary(bill),
                "date": bill.get("updateDate", ""),
                "agency": "U.S. Congress",
                "type": f"{bill.get('type', '').upper()} {bill.get('number', '')}",
                "url": bill.get("url", ""),
                "source": "Congress"
            })
        
        # Combine results
        all_results = formatted_federal + formatted_congress
        
        # Sort by date (most recent first)
        try:
            all_results.sort(key=lambda x: x.get('date', ''), reverse=True)
        except:
            pass
        
        return jsonify({
            "policies": all_results,
            "query": query,
            "total_count": len(all_results),
            "federal_count": len(formatted_federal),
            "congress_count": len(formatted_congress)
        })
    except Exception as e:
        print(f"❌ Policy search error for '{query}':", e)
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    print("🚀 CivicBridge Flask API running on http://localhost:5050")
    app.run(debug=True, host="localhost", port=5050)

"""
@app.route("/api/policyhub", methods=["GET"])
def get_policyhub():
    zip_code = request.args.get("zip")
    print("📥 PolicyHub request for ZIP:", zip_code)

    try:
        congress_bills = congress_client.get_recent_bills()[:5]
        federal_policies = fedreg_client.get_recent_policies()[:5]

        formatted = [
            {
                "title": p.get("title", "No title"),
                "summary": p.get("summary", p.get("abstract", "No summary available"))
            }
            for p in congress_bills + federal_policies
        ]

        return jsonify({"policies": formatted})
    except Exception as e:
        print("❌ PolicyHub error:", e)
        return jsonify({"error": str(e)}), 500
"""
