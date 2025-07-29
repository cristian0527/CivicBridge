"""
Congress.gov API integration for CivicBridge.

This module fetches live legislative data from Congress.gov API to provide users
with current information about bills, their status, voting records, and legislative activity.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv


class CongressAPIError(Exception):
    """Custom exception for Congress.gov API errors."""


class CongressClient:
    """Client for interacting with the Congress.gov API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('CONGRESS_API_KEY')
        if not self.api_key:
            raise CongressAPIError(
                "Congress.gov API key required. Get one from https://api.congress.gov/ "
                "and set CONGRESS_API_KEY environment variable or pass api_key parameter."
            )

        self.base_url = "https://api.congress.gov/v3"
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': self.api_key,
            'Accept': 'application/json'
        })
        self.logger = logging.getLogger(__name__)

    def get_recent_bills(
        self,
        congress: int = 119,  # Current Congress (118th = 2023-2024)
        limit: int = 20,
        bill_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """ Get recent bills introduced in Congress."""
        try:
            url = f"{self.base_url}/bill/{congress}"

            params = {
                'format': 'json',
                'limit': limit,
                'sort': 'updateDate+desc'
            }

            if bill_type:
                params['type'] = bill_type

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            bills = data.get('bills', [])

            self.logger.info("Retrieved %d recent bills from Congress %d", len(bills), congress)
            return bills

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch recent bills: {str(e)}"
            self.logger.error(error_msg)
            raise CongressAPIError(error_msg) from e

    def search_bills(
        self,
        query: str,
        congress: int = 119,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for bills by keyword.
        """
        try:
            url = f"{self.base_url}/bill/{congress}"

            params = {
                'format': 'json',
                'limit': limit,
                'q': query,
                'sort': 'updateDate+desc'
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            bills = data.get('bills', [])

            self.logger.info("Found %d bills matching '%s'", len(bills), query)
            return bills

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to search bills: {str(e)}"
            self.logger.error(error_msg)
            raise CongressAPIError(error_msg) from e

    def get_bill_details(
        self,
        congress: int,
        bill_type: str,
        bill_number: int
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific bill.
        """
        try:
            url = f"{self.base_url}/bill/{congress}/{bill_type}/{bill_number}"

            params = {'format': 'json'}

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            bill_data = data.get('bill', {})

            self.logger.info("Retrieved details for %s%d", bill_type.upper(), bill_number)
            return bill_data

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to get bill details: {str(e)}"
            self.logger.error(error_msg)
            raise CongressAPIError(error_msg) from e

    def get_bill_actions(
        self,
        congress: int,
        bill_type: str,
        bill_number: int
    ) -> List[Dict[str, Any]]:
        """
        Get the legislative actions/history for a bill.
        """
        try:
            url = f"{self.base_url}/bill/{congress}/{bill_type}/{bill_number}/actions"

            params = {'format': 'json', 'limit': 50}

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            actions = data.get('actions', [])

            self.logger.info("Retrieved %d actions for %s%d", len(actions), bill_type.upper(), bill_number)
            return actions

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to get bill actions: {str(e)}"
            self.logger.error(error_msg)
            raise CongressAPIError(error_msg) from e

    def get_bills_by_topic(self, topic: str) -> List[Dict[str, Any]]:
        """
        Get bills related to a specific topic.
        """
        # Define topic-specific search terms
        topic_terms = {
            'healthcare': 'health care medical insurance Medicare Medicaid hospital',
            'housing': 'housing rental mortgage affordable housing HUD',
            'education': 'education student loan school university college',
            'employment': 'employment job labor unemployment workforce',
            'taxes': 'tax taxation income revenue IRS',
            'environment': 'environment climate energy clean air water EPA',
            'transportation': 'transportation highway infrastructure transit',
            'immigration': 'immigration border visa citizenship DACA',
            'social_security': 'social security retirement disability benefits',
            'veterans': 'veterans military VA benefits healthcare'
        }

        search_term = topic_terms.get(topic.lower(), topic)
        return self.search_bills(search_term)

    def get_bill_status_summary(self, bill_data: Dict[str, Any]) -> str:
        """
        Generate a human-readable status summary for a bill.
        """
        latest_action = bill_data.get('latestAction', {})
        action_text = latest_action.get('text', 'No recent action')
        action_date = latest_action.get('actionDate', 'Unknown date')

        # Determine status based on latest action
        if 'passed' in action_text.lower():
            if 'house' in action_text.lower():
                bill_status = "✅ Passed House"
            elif 'senate' in action_text.lower():
                bill_status = "✅ Passed Senate"
            else:
                bill_status = "✅ Passed"
        elif 'introduced' in action_text.lower():
            bill_status = "📋 Introduced"
        elif 'committee' in action_text.lower():
            bill_status = "🏛️ In Committee"
        elif 'signed' in action_text.lower():
            bill_status = "✅ Signed into Law"
        elif 'vetoed' in action_text.lower():
            bill_status = "❌ Vetoed"
        else:
            bill_status = "⏳ In Progress"

        return f"{bill_status} - {action_date}"

    def format_bill_for_explanation(self, bill_data: Dict[str, Any]) -> str:
        """
        Format a bill for policy explanation by AI.
        """
        bill_title = bill_data.get('title', 'Unknown Bill')
        number = bill_data.get('number', '')
        bill_type = bill_data.get('type', '').upper()
        congress = bill_data.get('congress', '')

        # Bill identifier
        bill_id = f"{bill_type} {number}" if number else "Unknown Bill"

        # Sponsor information
        sponsors = bill_data.get('sponsors', [])
        sponsor_info = ""
        if sponsors:
            sponsor = sponsors[0]
            sponsor_name = sponsor.get('fullName', 'Unknown')
            party = sponsor.get('party', '')
            state = sponsor.get('state', '')
            sponsor_info = f"Sponsored by: {sponsor_name} ({party}-{state})"

        # Summary/title
        summary = bill_data.get('title', '')

        # Latest action
        latest_action = bill_data.get('latestAction', {})
        bill_status = self.get_bill_status_summary(bill_data)

        # Policy subjects
        subjects = bill_data.get('policyArea', {})
        policy_area = subjects.get('name', 'General') if subjects else 'General'

        # Build formatted text
        policy_text = f"Bill: {bill_id} ({congress}th Congress)\n"
        policy_text += f"Title: {bill_title}\n\n"

        if sponsor_info:
            policy_text += f"{sponsor_info}\n"

        policy_text += f"Policy Area: {policy_area}\n"
        policy_text += f"Current Status: {bill_status}\n\n"

        if latest_action.get('text'):
            policy_text += f"Latest Action: {latest_action['text']}\n\n"

        # Add summary if available
        if summary and summary != bill_title:
            policy_text += f"Summary: {summary}"
        else:
            policy_text += "This is a bill currently in Congress. "
            policy_text += "Detailed summary may be available as the bill progresses through the legislative process."

        return policy_text

    def get_trending_bills(self, days_back: int = 30) -> List[Dict[str, Any]]:
        """
        Get bills with recent activity (trending).
        """
        # Get recent bills and filter by update date
        recent_bills_data = self.get_recent_bills(limit=50)

        cutoff_date = datetime.now() - timedelta(days=days_back)

        trending_bills = []
        for bill_data in recent_bills_data:
            update_date_str = bill_data.get('updateDate', '')
            if update_date_str:
                try:
                    update_date = datetime.fromisoformat(update_date_str.replace('Z', '+00:00'))
                    if update_date.replace(tzinfo=None) >= cutoff_date:
                        trending_bills.append(bill_data)
                except ValueError:
                    continue  # Skip bills with invalid date format

        return trending_bills[:20]  # Return top 20 trending bills
    
    def get_member_details(self, bioguide_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific member of Congress."""
        try:
            url = f"{self.base_url}/member/{bioguide_id}"
            
            params = {'api_key': self.api_key, 'format': 'json'}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            member_data = data.get('member', {})
            
            self.logger.info(f"Retrieved member details for {bioguide_id}")
            return member_data
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to get member details for {bioguide_id}: {str(e)}"
            self.logger.error(error_msg)
            raise CongressAPIError(error_msg) from e

    def get_member_sponsored_legislation(
        self, 
        bioguide_id: str, 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get bills sponsored by a specific member."""
        try:
            url = f"{self.base_url}/member/{bioguide_id}/sponsored-legislation"
            
            params = {
                'api_key': self.api_key,
                'format': 'json',
                'limit': limit,
                'sort': 'latestAction.actionDate+desc'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            sponsored_legislation = data.get('sponsoredLegislation', [])
            
            self.logger.info(f"Retrieved {len(sponsored_legislation)} sponsored bills for {bioguide_id}")
            return sponsored_legislation
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to get sponsored legislation for {bioguide_id}: {str(e)}"
            self.logger.error(error_msg)
            # Return empty list instead of raising error for demo resilience
            return []

    def get_member_cosponsored_legislation(
        self, 
        bioguide_id: str, 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get bills cosponsored by a specific member."""
        try:
            url = f"{self.base_url}/member/{bioguide_id}/cosponsored-legislation"
            
            params = {
                'api_key': self.api_key,
                'format': 'json',
                'limit': limit,
                'sort': 'latestAction.actionDate+desc'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            cosponsored_legislation = data.get('cosponsoredLegislation', [])
            
            self.logger.info(f"Retrieved {len(cosponsored_legislation)} cosponsored bills for {bioguide_id}")
            return cosponsored_legislation
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to get cosponsored legislation for {bioguide_id}: {str(e)}"
            self.logger.error(error_msg)
            return []

    def get_member_voting_record(
    self, 
    bioguide_id: str, 
    limit: int = 50
) -> List[Dict[str, Any]]:
        """Get voting record for a specific member."""
        try:
        # Note: The Congress API doesn't have a direct voting record endpoint
        # This is a limitation we'll work around by getting their sponsored/cosponsored bills
        # For a quick demo, we'll return their legislative activity
        
            sponsored = self.get_member_sponsored_legislation(bioguide_id, limit=limit//2)
            cosponsored = self.get_member_cosponsored_legislation(bioguide_id, limit=limit//2)
            
            # Combine and format as "voting record" for demo purposes
            voting_record = []
            
            for bill in sponsored:
                if bill:  # Check if bill exists
                    latest_action = bill.get('latestAction') or {}
                    policy_area = bill.get('policyArea')
                    
                    bill_type = bill.get('type') or ''
                    bill_number = bill.get('number') or ''
                    
                    vote_item = {
                        'date': latest_action.get('actionDate', ''),
                        'bill_title': bill.get('title', 'Unknown Bill'),
                        'bill_number': f"{bill_type.upper()} {bill_number}" if bill_type else bill_number,
                        'position': 'Sponsored',
                        'latest_action': latest_action.get('text', 'No action recorded'),
                        'congress': str(bill.get('congress', '')),
                        'policy_area': policy_area.get('name', '') if policy_area else ''
                    }
                    voting_record.append(vote_item)
            
            for bill in cosponsored:
                if bill:  # Check if bill exists
                    latest_action = bill.get('latestAction') or {}
                    policy_area = bill.get('policyArea')
                    
                    bill_type = bill.get('type') or ''
                    bill_number = bill.get('number') or ''
                    
                    vote_item = {
                        'date': latest_action.get('actionDate', ''),
                        'bill_title': bill.get('title', 'Unknown Bill'),
                        'bill_number': f"{bill_type.upper()} {bill_number}" if bill_type else bill_number,
                        'position': 'Cosponsored',
                        'latest_action': latest_action.get('text', 'No action recorded'),
                        'congress': str(bill.get('congress', '')),
                        'policy_area': policy_area.get('name', '') if policy_area else ''
                    }
                    voting_record.append(vote_item)
            
            # Sort by date (most recent first)
            voting_record.sort(key=lambda x: x['date'], reverse=True)
            
            self.logger.info(f"Retrieved {len(voting_record)} voting record items for {bioguide_id}")
            return voting_record[:limit]
            
        except Exception as e:
            error_msg = f"Failed to get voting record for {bioguide_id}: {str(e)}"
            self.logger.error(error_msg)
            return []

    def format_member_activity_summary(self, bioguide_id: str) -> str:
        """Format a member's recent legislative activity for display."""
        try:
            member_details = self.get_member_details(bioguide_id)
            voting_record = self.get_member_voting_record(bioguide_id, limit=10)
            
            name = f"{member_details.get('firstName', '')} {member_details.get('lastName', '')}".strip()
            party = member_details.get('partyName', '')
            state = member_details.get('state', '')
            
            summary = f"Recent Legislative Activity for {name} ({party}-{state}):\n\n"
            
            if voting_record:
                summary += "Recent Bills:\n"
                for i, vote in enumerate(voting_record[:5], 1):
                    summary += f"{i}. {vote['position']}: {vote['bill_title'][:80]}...\n"
                    summary += f"   Status: {vote['latest_action'][:60]}...\n"
                    summary += f"   Date: {vote['date']}\n\n"
            else:
                summary += "No recent legislative activity found.\n"
            
            return summary
            
        except Exception as e:
            return f"Unable to generate activity summary for {bioguide_id}: {str(e)}"

def create_congress_client(api_key: Optional[str] = None) -> CongressClient:
    """
    Factory function to create a CongressClient instance.
    """
    return CongressClient(api_key)


# Example usage and testing
if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    try:
        client = create_congress_client()

        print("Testing Congress.gov API Client...")
        print("=" * 25)

        # Test 1: Get recent bills
        print("\n1. Getting recent bills...")
        recent_bills = client.get_recent_bills(limit=25)

        if recent_bills:
            print(f"Found {len(recent_bills)} recent bills")

            # Show first bill
            first_bill = recent_bills[0]
            print(f"\nSample bill:")
            print(f"Title: {first_bill.get('title', 'N/A')}")
            print(f"Number: {first_bill.get('type', '').upper()} {first_bill.get('number', 'N/A')}")
            print(f"Status: {client.get_bill_status_summary(first_bill)}")

            # Format for explanation
            formatted = client.format_bill_for_explanation(first_bill)
            print(f"\nFormatted for AI explanation:")
            print(formatted[:300] + "...")

        # Test 2: Search for healthcare bills
        print("\n2. Searching for healthcare bills...")
        healthcare_bills = client.search_bills('transporation', limit=25)
        print(f"Found {len(healthcare_bills)} transporation bills")

        if healthcare_bills:
            for bill_data in healthcare_bills:
                bill_title = bill_data.get('title', 'N/A')[:60]
                bill_status = client.get_bill_status_summary(bill_data)
                print(f"- {bill_title}... | {bill_status}")

        # Test 3: Get bills by topic
        print("\n3. Getting education-related bills...")
        education_bills = client.get_bills_by_topic('education')
        print(f"Found {len(education_bills)} education bills")

        # Test 4: Get trending bills
        print("\n4. Getting trending bills...")
        trending = client.get_trending_bills(days_back=30)
        print(f"Found {len(trending)} trending bills")

        print("\n5. Testing representative data...")
        
        # Test with some known bioguide IDs (these are real representatives)
        test_bioguides = [
            "S000148",   # Chuck Schumer
            "D000563",  # Dick Durbin (Senator)
            "B001135",  # Richard Blumenthal (Senator) 
            "D000620"   # Rosa DeLauro (Representative)
        ]
        
        for bioguide_id in test_bioguides:
            try:
                print(f"\n--- Testing {bioguide_id} ---")
                
                # Get member details
                member_details = client.get_member_details(bioguide_id)
                if member_details:
                    name = f"{member_details.get('firstName', '')} {member_details.get('lastName', '')}".strip()
                    party = member_details.get('partyName', '')
                    state = member_details.get('state', '')
                    print(f"✅ Member: {name} ({party}-{state})")
                
                # Get sponsored legislation
                sponsored = client.get_member_sponsored_legislation(bioguide_id, limit=3)
                print(f"✅ Sponsored bills: {len(sponsored)}")
                
                # Get voting record (our combined approach)
                voting_record = client.get_member_voting_record(bioguide_id, limit=5)
                print(f"✅ Legislative activity: {len(voting_record)} items")
                
                if voting_record:
                    print("Recent activity:")
                    for vote in voting_record[:2]:
                        print(f"  - {vote['position']}: {vote['bill_title'][:50]}...")
                
                break  # Just test the first working one for now
                
            except CongressAPIError as e:
                print(f"❌ Error testing {bioguide_id}: {e}")
                continue
            except Exception as e:
                print(f"❌ Unexpected error testing {bioguide_id}: {e}")
                continue

    except CongressAPIError as e:
        print(f"Congress API error: {e}")
        print("\nMake sure to:")
        print("1. Get an API key from https://api.congress.gov/")
        print("2. Set CONGRESS_API_KEY environment variable")
    except Exception as e:
        print(f"Unexpected error: {e}")
    