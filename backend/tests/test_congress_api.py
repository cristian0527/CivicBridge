"""Test cases for Congress.gov API integration."""

import unittest
import sys
import os
from unittest.mock import patch, Mock

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from congress_api import create_congress_client, CongressAPIError


class TestCongressAPI(unittest.TestCase):
    """Test cases for Federal Register API integration."""

    def setUp(self):
        """Set up test client."""
        self.client = create_congress_client()

    def test_client_initialization(self):
        """Test that client initializes correctly."""
        self.assertIsNotNone(self.client)
        self.assertEqual(self.client.base_url,
                         "https://api.congress.gov/v3")

    @patch('congress_api.requests.Session.get')
    def test_search_bills_success(self, mock_get):
        """Test successful bill search."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'bills': [
                {
                    'title': 'Test Healthcare Bill',
                    'number': '1234',
                    'type': 'hr',
                    'congress': '118',
                    'latestAction': {
                        'text': 'Introduced in House',
                        'actionDate': '2024-01-15'
                    },
                    'sponsors': [{'fullName': 'Test Rep', 'party': 'D', 'state': 'CA'}]
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test search
        results = self.client.search_bills('healthcare')

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Test Healthcare Bill')
        self.assertEqual(results[0]['number'], '1234')

    @patch('congress_api.requests.Session.get')
    def test_search_bills_api_error(self, mock_get):
        """Test API error handling in bill search."""
        mock_get.side_effect = Exception("API Error")

        with self.assertRaises(CongressAPIError):
            self.client.search_bills('test')

    @patch('congress_api.requests.Session.get')
    def test_get_bill_details_success(self, mock_get):
        """Test successful bill detail retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'bill': {
                'title': 'Detailed Bill',
                'number': '5678',
                'type': 'hr',
                'congress': '118',
                'summary': 'Detailed bill summary'
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.get_bill_details(118, 'hr', 5678)

        self.assertEqual(result['title'], 'Detailed Bill')
        self.assertEqual(result['number'], '5678')

    def test_format_bill_for_explanation(self):
        """Test bill formatting for AI explanation."""
        test_bill = {
            'title': 'Test Climate Change Bill',
            'number': '1111',
            'type': 'hr',
            'congress': '118',
            'sponsors': [{'fullName': 'Jane Doe', 'party': 'D', 'state': 'NY'}],
            'latestAction': {
                'text': 'Passed House',
                'actionDate': '2024-02-01'
            },
            'policyArea': {'name': 'Environmental Protection'}
        }

        formatted = self.client.format_bill_for_explanation(test_bill)

        self.assertIn('Test Climate Change Bill', formatted)
        self.assertIn('HR 1111', formatted)
        self.assertIn('Jane Doe', formatted)
        self.assertIn('Environmental Protection', formatted)

    def test_get_bill_status_summary_passed(self):
        """Test bill status summary for passed bill."""
        test_bill = {
            'latestAction': {
                'text': 'Passed House by voice vote',
                'actionDate': '2024-01-20'
            }
        }

        status = self.client.get_bill_status_summary(test_bill)
        self.assertIn('Passed House', status)
        self.assertIn('2024-01-20', status)

    def test_get_bill_status_summary_introduced(self):
        """Test bill status summary for introduced bill."""
        test_bill = {
            'latestAction': {
                'text': 'Introduced in House',
                'actionDate': '2024-01-15'
            }
        }

        status = self.client.get_bill_status_summary(test_bill)
        self.assertIn('Introduced', status)

    def test_get_bills_by_topic_healthcare(self):
        """Test topic-based bill search for healthcare."""
        with patch.object(self.client, 'search_bills') as mock_search:
            mock_search.return_value = [{'title': 'Healthcare Bill'}]

            results = self.client.get_bills_by_topic('healthcare')

            # Verify search was called with healthcare-related terms
            mock_search.assert_called_once()
            call_args = mock_search.call_args
            self.assertIn('health care medical', call_args[0][0])

    def test_get_bills_by_topic_unknown(self):
        """Test topic search with unknown topic."""
        with patch.object(self.client, 'search_bills') as mock_search:
            mock_search.return_value = []

            results = self.client.get_bills_by_topic('unknown_topic')

            # Should still call search with the topic name
            mock_search.assert_called_once()
            call_args = mock_search.call_args
            self.assertEqual(call_args[0][0], 'unknown_topic')

    @patch('congress_api.requests.Session.get')
    def test_get_recent_bills(self, mock_get):
        """Test fetching recent bills."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'bills': [
                {
                    'title': 'Recent Bill',
                    'type': 'hr',
                    'number': '999',
                    'updateDate': '2024-01-10'
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        results = self.client.get_recent_bills(limit=5)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Recent Bill')

    def test_format_bill_minimal_data(self):
        """Test formatting bill with minimal data."""
        minimal_bill = {
            'title': 'Minimal Bill'
        }

        formatted = self.client.format_bill_for_explanation(minimal_bill)

        self.assertIn('Minimal Bill', formatted)
        self.assertIn('Bill:', formatted)


if __name__ == "__main__":
    unittest.main()