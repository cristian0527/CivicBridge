"""
Google GenAI integration for CivicBridge policy explanations.

This module handles the AI-powered generation of personalized, plain-English
explanations of government policies based on user context.
"""

import os
import re
import logging
from typing import Optional, Dict, Any
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List

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
        immigration = user_context.get("immigration_status", "N/A")
        housing = user_context.get("housing_status", "N/A")
        healthcare = user_context.get("healthcare_access", "N/A")

        missing_fields = [
            k for k in ["zip_code", "role", "age", "income_bracket", "housing_status", "healthcare_access", "immigration_status"]
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
- Income: {income}
- Housing: {housing}
- Immigration Status: {immigration}
- Healthcare: {healthcare}

POLICY TO EXPLAIN:
{policy_text}

INSTRUCTIONS:
1. Write in simple, conversational language (8th-grade level)
2. Keep response to 2-3 short paragraphs maximum. Please keep response under 200 words.
3. Focus on practical impact for this specific user
4. Be direct and factual
5. NO bullet points, asterisks, or special formatting
6. NO bold text or markdown formatting
7. Write in plain paragraph form only

RESPONSE FORMAT:
Start with a one-sentence summary, then provide details about personal impact.

REMINDER: Please have the structure of explaining what the policy does, then explain how it affects someone. If user provides information, discuss how it affects them. Keep it brief and easy to understand
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
    
    # NEW METHODS FOR CHAT RESPONSE GENERATION
    def _fetch_representative_data(self, zip_code: str, geocodio_client, congress_client) -> List[Dict]:
        """Fetch representative data for a ZIP code."""
        try:
            reps = geocodio_client.get_representatives(zip_code)
        
            enhanced_reps = []
            for rep in reps[:3]:  # Limit to 3 for performance
                bioguide_id = rep.get('bioguide_id')
                if bioguide_id:
                # Get recent legislative activity
                    recent_activity = congress_client.get_member_voting_record(bioguide_id, limit=5)
                    rep['recent_activity'] = recent_activity
                enhanced_reps.append(rep)
        
            return enhanced_reps
        except Exception as e:
            self.logger.error(f"Error fetching representative data: {e}")
            return []

    def generate_chat_response(
        self,
        user_message: str,
        user_context: Dict[str, Any]= None,
        chat_history: List[Dict[str, str]] = None,
        max_tokens: int = 500
    ):
        """Generate a chat response based on user input and context."""
        try:
            prompt = self._build_chat_prompt(user_message, user_context, chat_history)

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

            response = self.model.generate_content(prompt,
                safety_settings=safety_settings,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.4,
                )
            )

            if not response.text:
                raise PolicyExplainError("Empty response from GenAI API")
            
            self.logger.info("Successfully generated chat response")
            return response.text.strip()
        except Exception as original_error:
            error_msg = f"Failed to generate chat response: {str(original_error)}"
            self.logger.error("Error generating chat response: %s", str(original_error))
            raise PolicyExplainError(error_msg) from original_error

    # Build a prompt for chat response generation
    # This is similar to the policy explanation prompt but tailored for chat interactions
    # It includes user context and recent chat history to provide relevant context for the AI
    # This helps the AI generate responses that are more personalized and relevant to the user's situation
    def _build_chat_prompt(
        self,
        user_message: str,
        user_context: Dict[str, Any] = None,
        chat_history: List[Dict[str, str]] = None
    ) -> str:
        """ Build a prompt for civicbridge chat response."""
        prompt = """
                You are CivicBridge Assistant, a helpful civic education AI that explains government, policies, 
                and political processes in simple terms. You help people understand how government works and 
                how to engage civically in a very understandable way.

                GUIDELINES:
                1. Keep responses conversational and accessible (8th-grade reading level)
                2. NO bullet points, asterisks, or special formatting
                3. Write in plain paragraph form only
                4. Stay factual and non-partisan
                5. Focus on education, not advocacy
                6. If asked about specific policies, provide balanced explanations
                7. Encourage civic participation (voting, contacting reps, staying informed)
                8. If you don't know something specific, say so and suggest reliable sources
            """
        
        # Add user context if available
        if user_context:
            zip_code = user_context.get("zip_code", "")
            role = user_context.get("role", "general citizen")
            if zip_code or role:
                prompt += f"\nUser Context: "
                if zip_code:
                    prompt += f"Zip Code: {zip_code} "
                if role:
                    prompt += f"Role: {role} "
                prompt += "\n\n"
        
        # Add chat history if available
        if chat_history:
            prompt += "Chat History:\n"
            for message in chat_history[-15:]: # Limit to last 15 messages
                prompt += f"User: {message.get('user_message', '')}\n"
                prompt += f"Assistant: {message.get('bot_response', '')}\n"
        prompt += "\n"

        # Add current user message
        prompt += f"User's current message: {user_message}\n\n"
        prompt += "Provide a helpful, educational response based on the above context and guidelines. Respond helpfully in 2-3 short paragraphs. No formatting or bullet points"
        return prompt
    
    # Policy Display Summaries
    def generate_policy_summary(
        self,
        policy_text: str,
        max_sentences: int = 4
    ) -> str:
        """Generate a concise, brief summary of a policy for display."""
        try:
            prompt = f"""
            Summarize the following government policy, or bill, in 3-{max_sentences} clear, simple sentences, focusing on the key points and implications for the general public. 
            Focus on what the policy does, who it affects, and any important details.
            
            Policy: {policy_text}

            Summary: ({max_sentences} sentences max. Depending on the policy, it may be less than {max_sentences} sentences or more than {max_sentences} sentences. Though, keep it short and understable)
            """
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=150,
                    temperature=0.3,
                )
            )

            if not response.text:
                raise PolicyExplainError("Empty response from GenAI API")

            self.logger.info("Successfully generated policy summary")
            return response.text.strip()
        except Exception as e:
            self.logger.error(f"Error generating policy summary: {e}")
            return policy_text[:200] + "..." if len(policy_text) > 200 else policy_text  # Fallback to first 200 chars if error occurs
        
    def _detect_intent(self, user_message: str) -> Dict[str, Any]:
        """Detect what type of government data the user is asking about."""
        message_lower = user_message.lower()
            
        intent = {"type": "general", "entities": []}
            
        # Detect bill mentions (HR 123, H.R. 123, S. 456, etc.)
        bill_patterns = [
                r'\b(?:hr|h\.r\.)\s*(\d+)\b',  # HR 123 or H.R. 123
                r'\bs\.?\s*(\d+)\b',           # S 456 or S. 456
                r'\b(?:house|senate)\s*bill\s*(\d+)\b'  # House Bill 123
            ]
            
        for pattern in bill_patterns:
            matches = re.findall(pattern, message_lower)
            if matches:
                intent["type"] = "bill_inquiry"
                intent["entities"].extend([{"type": "bill_number", "value": match} for match in matches])
            
        # Detect representative mentions
        rep_keywords = ["representative", "congressman", "congresswoman", "senator", "rep"]
        if any(keyword in message_lower for keyword in rep_keywords):
            if intent["type"] == "general":
                intent["type"] = "representative_inquiry"
            
        # Detect policy/legislation keywords
        policy_keywords = ["policy", "legislation", "law", "act", "bill"]
        if any(keyword in message_lower for keyword in policy_keywords):
            if intent["type"] == "general":
                intent["type"] = "policy_inquiry"
            
        # Detect email writing requests
        email_keywords = ["write", "email", "letter", "contact", "message"]
        if any(keyword in message_lower for keyword in email_keywords):
            intent["type"] = "email_writing"
            
        return intent
    
    def _fetch_bill_data(self, bill_number: str, congress_client) -> Optional[Dict]:
        """Fetch bill data from Congress API."""
        try:
            # Search for bills with this number
            bills = congress_client.search_bills(f"bill {bill_number}", limit=5)
                
            if bills:
                # Get the most recent/relevant bill
                bill = bills[0]
                bill_details = congress_client.get_bill_details(
                    bill.get('congress', 119),
                    bill.get('type', 'hr'),
                    bill.get('number', bill_number))
                return {
                    "title": bill.get('title', 'Unknown Bill'),
                    "number": f"{bill.get('type', '').upper()} {bill.get('number', '')}",
                    "status": congress_client.get_bill_status_summary(bill),
                    "summary": bill_details.get('summary', 'No summary available'),
                    "sponsor": bill.get('sponsors', [{}])[0].get('fullName', 'Unknown') if bill.get('sponsors') else 'Unknown'
                    }
        except Exception as e:
            self.logger.error(f"Error fetching bill data: {e}")
        
        return None
        
    def generate_enhanced_chat_response(
        self,
        user_message: str,
        user_context: Dict[str, Any] = None,
        chat_history: List[Dict[str, str]] = None,
        congress_client=None,
        geocodio_client=None,
        max_tokens: int = 600) -> str:
        """Generate a smart chat response that can fetch and use government data."""
        try:
            # Detect what the user is asking about
            intent = self._detect_intent(user_message)
            
            # Fetch relevant data based on intent
            context_data = {}
            
            if intent["type"] == "bill_inquiry" and congress_client:
                for entity in intent["entities"]:
                    if entity["type"] == "bill_number":
                        bill_data = self._fetch_bill_data(entity["value"], congress_client)
                        if bill_data:
                            context_data["bill"] = bill_data
                            break
            
            elif intent["type"] in ["representative_inquiry", "policy_inquiry"]:
                zip_code = user_context.get("zip_code") if user_context else None
                if zip_code and geocodio_client and congress_client:
                    rep_data = self._fetch_representative_data(zip_code, geocodio_client, congress_client)
                    if rep_data:
                        context_data["representatives"] = rep_data
            
            # Build enhanced prompt with data
            prompt = self._build_smart_chat_prompt(
                user_message, 
                user_context, 
                chat_history, 
                intent, 
                context_data
            )
            
            # Generate response
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }

            response = self.model.generate_content(
                prompt,
                safety_settings=safety_settings,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.4,
                )
            )

            if not response.text:
                raise PolicyExplainError("Empty response from GenAI API")
            
            self.logger.info(f"Generated enhanced chat response for intent: {intent['type']}")
            return response.text.strip()
        
        except Exception as e:
            self.logger.error(f"Error generating enhanced chat response: {e}")
                # Fallback to regular chat response
            return self.generate_chat_response(user_message, user_context, chat_history, max_tokens)

    def _build_smart_chat_prompt(
        self,
        user_message: str,
        user_context: Dict[str, Any] = None,
        chat_history: List[Dict[str, str]] = None,
        intent: Dict[str, Any] = None,
        context_data: Dict[str, Any] = None) -> str:
        """Build an enhanced prompt that includes relevant government data."""
            
        prompt = """
            You are CivicBridge Assistant, a helpful AI that explains government, policies, and political processes in simple, 8th-grade level language. You help people understand how government works and how to engage civically.

            GUIDELINES:
            1. Keep responses conversational and accessible (8th-grade reading level)
            2. Stay factual and non-partisan
            3. Focus on education, not advocacy
            4. If asked about specific policies, provide balanced explanations
            5. Encourage civic participation (voting, contacting reps, staying informed)
            6. If you don't know something specific, say so and suggest reliable sources
            7. For bill explanations, focus on what it does and who it affects
            8. For email writing, create professional, respectful, and informative content
            """
            
            # Add user context
        if user_context:
            zip_code = user_context.get("zip_code", "")
            role = user_context.get("role", "general citizen")
            if zip_code or role:
                prompt += f"\nUser Context: "
                if zip_code:
                    prompt += f"ZIP Code: {zip_code} "
                if role:
                    prompt += f"Role: {role} "
                prompt += "\n"
            
            # Add relevant data based on what user is asking about
        if context_data:
            prompt += "\nRELEVANT DATA:\n"
                
            if "bill" in context_data:
                bill = context_data["bill"]
                prompt += f"""
                    BILL INFORMATION:
                    - Title: {bill['title']}
                    - Number: {bill['number']}
                    - Sponsor: {bill['sponsor']}
                    - Status: {bill['status']}
                    - Summary: {bill['summary'][:300]}...
                    """
                
            if "representatives" in context_data:
                prompt += "\nREPRESENTATIVES:\n"
                for rep in context_data["representatives"][:2]:  # Limit for prompt length
                    prompt += f"""
                        - {rep['name']} ({rep['party']}) - {rep['chamber']}
                        Recent Activity: {len(rep.get('recent_activity', []))} recent bills
                        """
            
            # Add chat history
        if chat_history:
            prompt += "\nRecent Chat History:\n"
            for message in chat_history[-10:]:  # Last 10 messages
                prompt += f"User: {message.get('user_message', '')}\n"
                prompt += f"Assistant: {message.get('bot_response', '')}\n"
            
            # Add current message and specific instructions based on intent
        prompt += f"\nUser's current message: {user_message}\n\n"
            
        if intent and intent["type"] == "bill_inquiry":
            prompt += "The user is asking about a specific bill. Use the bill data provided above to give a clear, factual explanation of what the bill does and who it affects.\n"
        elif intent and intent["type"] == "email_writing":
            prompt += "The user wants to write an email. Create a professional, respectful template they can customize. Include proper structure (greeting, body, closing) and talking points.\n"
        elif intent and intent["type"] == "representative_inquiry":
            prompt += "The user is asking about their representatives. Use the representative data provided to give helpful information about who represents them.\n"
            
        prompt += "Provide a helpful, educational response:"
            
        return prompt

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
