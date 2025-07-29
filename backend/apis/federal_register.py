"""
Federal Register API integration for CivicBridge.

This module fetches real government policies and documents from the Federal Register API
to provide users with current policy information for explanation.
"""

import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


class FederalRegisterError(Exception):
    """Custom exception for Federal Register API errors."""


class FederalRegisterClient:
    """Client for interacting with the Federal Register API."""

    def __init__(self):
        """Initialize the Federal Register API client."""
        self.base_url = "https://www.federalregister.gov/api/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CivicBridge/1.0 (Policy Explanation Tool)',
            'Accept': 'application/json'
        })
        self.logger = logging.getLogger(__name__)

    def search_documents(
        self,
        query: str,
        document_types: Optional[List[str]] = None,
        agencies: Optional[List[str]] = None,
        days_back: int = 30,
        per_page: int = 5
    ) -> List[Dict[str, Any]]:

        # Search for documents in the Federal Register.

        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)

            params = {
                'conditions[term]': query,
                'conditions[publication_date][gte]': start_date.strftime('%Y-%m-%d'),
                'conditions[publication_date][lte]': end_date.strftime('%Y-%m-%d'),
                'per_page': per_page,
                'order': 'newest'
            }

            # Add document type filters
            if document_types:
                params['conditions[type][]'] = document_types

            # Add agency filters
            if agencies:
                params['conditions[agencies][]'] = agencies

            url = f"{self.base_url}/documents.json"
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            documents = data.get('results', [])

            self.logger.info(
                f"Found {len(documents)} documents for query: {query}")
            return documents

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to search Federal Register: {str(e)}"
            self.logger.error(error_msg)
            raise FederalRegisterError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error searching Federal Register: {str(e)}"
            self.logger.error(error_msg)
            raise FederalRegisterError(error_msg) from e

    def get_document_details(self, document_number: str) -> Dict[str, Any]:

        # Get detailed information about a specific document.

        try:
            url = f"{self.base_url}/documents/{document_number}.json"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            document = response.json()
            self.logger.info(
                f"Retrieved document details for: {document_number}")
            return document

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to get document {document_number}: {str(e)}"
            self.logger.error(error_msg)
            raise FederalRegisterError(error_msg) from e

    def get_recent_rules(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Get recent final rules that might affect citizens.

        Returns:
            List of recent rule documents
        """
        return self.search_documents(
            query="",
            document_types=['RULE'],
            days_back=days_back,
            per_page=10
        )

    def get_policy_by_topic(self, topic: str) -> List[Dict[str, Any]]:
        """
        Search for policies related to a specific topic.

        Args:
            topic: Policy topic (e.g., "healthcare", "housing", "education")

        Returns:
            List of relevant policy documents
        """
        # Define topic-specific search terms
        topic_terms = {
            'healthcare': 'health care medical insurance Medicare Medicaid',
            'housing': 'housing rental mortgage foreclosure HUD',
            'education': 'education student loan school university college',
            'employment': 'employment job work labor unemployment',
            'taxes': 'tax taxation IRS income deduction credit',
            'environment': 'environment climate energy EPA pollution',
            'transportation': 'transportation highway aviation FAA DOT',
            'immigration': 'immigration visa citizenship border',
            'social_security': 'social security disability benefits SSA',
            'veterans': 'veterans VA military benefits'
        }

        search_term = topic_terms.get(topic.lower(), topic)

        return self.search_documents(
            query=search_term,
            document_types=None,
            days_back=365,
            per_page=5
        )

    def format_document_for_explanation(self, document: Dict[str, Any]) -> str:
        """
        Format a Federal Register document for policy explanation.
        Returns:
            Formatted policy text suitable for AI explanation
        """
        title = document.get('title', 'Unknown Policy')
        abstract = document.get('abstract', '')
        agency_names = ', '.join([agency.get('name', '')
                                 for agency in document.get('agencies', [])])
        publication_date = document.get('publication_date', '')
        document_number = document.get('document_number', '')

        # Build a comprehensive policy description
        policy_text = f"Title: {title}\n\n"

        if agency_names:
            policy_text += f"Agency: {agency_names}\n"

        if publication_date:
            policy_text += f"Published: {publication_date}\n"

        if document_number:
            policy_text += f"Document Number: {document_number}\n"

        policy_text += "\n"

        if abstract:
            policy_text += f"Summary: {abstract}"
        else:
            policy_text += "This is a federal regulation or policy document. "
            policy_text += "Detailed summary not available in the Federal Register entry."

        return policy_text

    def get_trending_policies(self) -> List[Dict[str, Any]]:
        """
        Get trending/popular policies based on recent activity.

        Returns:
            List of trending policy documents
        """
        # Get recent rules and notices that might be trending
        recent_docs = self.search_documents(
            query="",
            document_types=['RULE', 'NOTICE'],
            days_back=14,
            per_page=20
        )

        # Sort by comment count or other engagement metrics if available and return most recent
        return recent_docs[:10]


def create_federal_register_client() -> FederalRegisterClient:
    """
    Factory function to create a FederalRegisterClient instance.

    Returns:
        Configured FederalRegisterClient instance
    """
    return FederalRegisterClient()


# Example usage and testing
if __name__ == "__main__":
    import json

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    try:
        client = create_federal_register_client()

        print("Testing Federal Register API Client...")
        print("=" * 50)

        # Test 1: Search for healthcare policies
        print("\n1. Searching for healthcare policies...")
        healthcare_docs = client.get_policy_by_topic('healthcare')

        if healthcare_docs:
            print(f"Found {len(healthcare_docs)} healthcare documents")

            # Show first document
            first_doc = healthcare_docs[0]
            print(f"\nSample document:")
            print(f"Title: {first_doc.get('title', 'N/A')}")
            print(
                f"Agency: {', '.join([a.get('name', '') for a in first_doc.get('agencies', [])])}")
            print(f"Date: {first_doc.get('publication_date', 'N/A')}")

            # Format for explanation
            formatted = client.format_document_for_explanation(first_doc)
            print(f"\nFormatted for AI explanation:")
            print(formatted[:300] + "...")

        # Test 2: Get recent rules
        print("\n2. Getting recent rules...")
        recent_rules = client.get_recent_rules(days_back=7)
        print(f"Found {len(recent_rules)} recent rules")

        # Test 3: Search for specific term
        print("\n3. Searching for 'student loan' policies...")
        loan_docs = client.search_documents('student loan', days_back=60)
        print(f"Found {len(loan_docs)} student loan documents")

        if loan_docs:
            sample_doc = loan_docs[0]
            print(f"Sample: {sample_doc.get('title', 'N/A')}")

    except FederalRegisterError as e:
        print(f"Federal Register API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
