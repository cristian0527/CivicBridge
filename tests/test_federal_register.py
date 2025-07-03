from federal_register import create_federal_register_client, FederalRegisterError
from unittest.mock import patch, Mock
import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestFederalRegister(unittest.TestCase):
    """Test cases for Federal Register API integration."""

    def setUp(self):
        """Set up test client."""
        self.client = create_federal_register_client()

    def test_client_initialization(self):
        """Test that client initializes correctly."""
        self.assertIsNotNone(self.client)
        self.assertEqual(self.client.base_url,
                         "https://www.federalregister.gov/api/v1")

    @patch('federal_register.requests.Session.get')
    def test_search_documents_success(self, mock_get):
        """Test successful document search."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'results': [
                {
                    'title': 'Test Policy',
                    'document_number': '2024-12345',
                    'publication_date': '2024-01-15',
                    'agencies': [{'name': 'Test Agency'}],
                    'abstract': 'Test policy abstract'
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test search
        results = self.client.search_documents('healthcare')

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Test Policy')
        self.assertEqual(results[0]['document_number'], '2024-12345')

    @patch('federal_register.requests.Session.get')
    def test_search_documents_api_error(self, mock_get):
        """Test API error handling in document search."""
        mock_get.side_effect = Exception("API Error")

        with self.assertRaises(FederalRegisterError):
            self.client.search_documents('test')

    @patch('federal_register.requests.Session.get')
    def test_get_document_details_success(self, mock_get):
        """Test successful document detail retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'title': 'Detailed Policy',
            'document_number': '2024-67890',
            'abstract': 'Detailed abstract',
            'full_text_xml_url': 'https://example.com/doc.xml'
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.get_document_details('2024-67890')

        self.assertEqual(result['title'], 'Detailed Policy')
        self.assertEqual(result['document_number'], '2024-67890')

    def test_format_document_for_explanation(self):
        """Test document formatting for AI explanation."""
        test_document = {
            'title': 'Test Healthcare Policy',
            'abstract': 'This policy expands healthcare access.',
            'agencies': [{'name': 'Department of Health'}],
            'publication_date': '2024-01-15',
            'document_number': '2024-12345'
        }

        formatted = self.client.format_document_for_explanation(test_document)

        self.assertIn('Test Healthcare Policy', formatted)
        self.assertIn('Department of Health', formatted)
        self.assertIn('2024-01-15', formatted)
        self.assertIn('This policy expands healthcare access.', formatted)

    def test_get_policy_by_topic_healthcare(self):
        """Test topic-based policy search for healthcare."""
        with patch.object(self.client, 'search_documents') as mock_search:
            mock_search.return_value = [{'title': 'Healthcare Policy'}]

            results = self.client.get_policy_by_topic('healthcare')

            # Verify search was called with healthcare-related terms
            mock_search.assert_called_once()
            call_args = mock_search.call_args
            self.assertIn('health care medical', call_args[1]['query'])

    def test_get_policy_by_topic_unknown(self):
        """Test topic search with unknown topic."""
        with patch.object(self.client, 'search_documents') as mock_search:
            mock_search.return_value = []

            results = self.client.get_policy_by_topic('unknown_topic')

            # Should still call search with the topic name
            mock_search.assert_called_once()
            call_args = mock_search.call_args
            self.assertEqual(call_args[1]['query'], 'unknown_topic')

    @patch('federal_register.requests.Session.get')
    def test_get_recent_rules(self, mock_get):
        """Test fetching recent rules."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'results': [
                {
                    'title': 'Recent Rule',
                    'type': 'RULE',
                    'publication_date': '2024-01-10'
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        results = self.client.get_recent_rules(days_back=7)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Recent Rule')

    def test_format_document_minimal_data(self):
        """Test formatting document with minimal data."""
        minimal_doc = {
            'title': 'Minimal Policy'
        }

        formatted = self.client.format_document_for_explanation(minimal_doc)

        self.assertIn('Minimal Policy', formatted)
        self.assertIn('Title:', formatted)


if __name__ == "__main__":
    unittest.main()
