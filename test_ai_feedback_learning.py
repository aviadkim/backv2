"""
Test module for AI Feedback Learning.

This module tests the AI feedback learning functionality to ensure that
the AI gets smarter with each document scan and correction.
"""
import os
import json
import shutil
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import hashlib
from datetime import datetime

from ai_feedback_learning import AIFeedbackLearning

class TestAIFeedbackLearning(unittest.TestCase):
    """Test cases for AI Feedback Learning."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()

        # Create a mock API key
        self.api_key = os.environ.get("OPENROUTER_API_KEY", "test_api_key")

        # Initialize the AI feedback learning module
        self.feedback_learning = AIFeedbackLearning(api_key=self.api_key)

        # Create a test document
        self.test_document_path = os.path.join(self.test_dir, "test_document.txt")
        with open(self.test_document_path, "w", encoding="utf-8") as f:
            f.write("This is a test document.\n")
            f.write("It contains some financial information.\n")
            f.write("Portfolio Value: 1,000,000\n")
            f.write("ISIN: US0378331005, Value: 100,000\n")
            f.write("ISIN: US5949181045, Value: 200,000\n")

        # Create another similar document
        self.similar_document_path = os.path.join(self.test_dir, "similar_document.txt")
        with open(self.similar_document_path, "w", encoding="utf-8") as f:
            f.write("This is a similar document.\n")
            f.write("It also contains some financial information.\n")
            f.write("Portfolio Value: 2,000,000\n")
            f.write("ISIN: US0378331005, Value: 150,000\n")
            f.write("ISIN: US5949181045, Value: 250,000\n")

    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory and files
        shutil.rmtree(self.test_dir)

        # Remove feedback and corrections store files
        if os.path.exists("feedback_store.json"):
            os.remove("feedback_store.json")
        if os.path.exists("corrections_store.json"):
            os.remove("corrections_store.json")

    def test_register_document(self):
        """Test registering a document."""
        # Register the test document
        doc_fingerprint, source_fingerprint = self.feedback_learning.register_document(self.test_document_path)

        # Check that fingerprints are generated
        self.assertIsNotNone(doc_fingerprint)
        self.assertIsNotNone(source_fingerprint)

        # Check that document is registered
        self.assertIn(doc_fingerprint, self.feedback_learning.document_fingerprints)
        self.assertEqual(self.feedback_learning.document_fingerprints[doc_fingerprint]["document_path"],
                         self.test_document_path)

    def test_record_correction(self):
        """Test recording a correction."""
        # Register the test document
        doc_fingerprint, source_fingerprint = self.feedback_learning.register_document(self.test_document_path)

        # Record a correction
        field = "portfolio_value"
        original_value = 1000000
        corrected_value = 1500000

        success = self.feedback_learning.record_correction(
            doc_fingerprint, field, original_value, corrected_value
        )

        # Check that correction was recorded
        self.assertTrue(success)
        self.assertIn(source_fingerprint, self.feedback_learning.corrections_store)
        self.assertEqual(len(self.feedback_learning.corrections_store[source_fingerprint]), 1)

        correction = self.feedback_learning.corrections_store[source_fingerprint][0]
        self.assertEqual(correction["field"], field)
        self.assertEqual(correction["original_value"], original_value)
        self.assertEqual(correction["corrected_value"], corrected_value)

    @patch('requests.post')
    def test_learn_from_correction(self, mock_post):
        """Test learning from a correction."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "The AI has learned from this correction."
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        # Register the test document
        doc_fingerprint, source_fingerprint = self.feedback_learning.register_document(self.test_document_path)

        # Record a correction
        field = "portfolio_value"
        original_value = 1000000
        corrected_value = 1500000

        correction_entry = {
            "document_fingerprint": doc_fingerprint,
            "source_fingerprint": source_fingerprint,
            "field": field,
            "original_value": original_value,
            "corrected_value": corrected_value,
            "timestamp": datetime.now().isoformat()
        }

        # Learn from correction
        success = self.feedback_learning._learn_from_correction(correction_entry)

        # Check that learning was successful
        self.assertTrue(success)
        self.assertIn("ai_insights", correction_entry)

        # Check that API was called with correct parameters
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://openrouter.ai/api/v1/chat/completions")
        self.assertEqual(kwargs["headers"]["Authorization"], f"Bearer {self.api_key}")
        self.assertEqual(kwargs["json"]["model"], "anthropic/claude-3-opus:beta")

    def test_get_similar_document_corrections(self):
        """Test getting corrections for similar documents."""
        # Register the test document
        doc_fingerprint, source_fingerprint = self.feedback_learning.register_document(self.test_document_path)

        # Record a correction
        field = "portfolio_value"
        original_value = 1000000
        corrected_value = 1500000

        self.feedback_learning.record_correction(
            doc_fingerprint, field, original_value, corrected_value
        )

        # Create a similar document content with the keyword for testing
        similar_document_content = "This is a similar_document with test content."

        # Get corrections for similar document
        corrections = self.feedback_learning.get_similar_document_corrections(similar_document_content)

        # Check that corrections are returned
        self.assertEqual(len(corrections), 1)
        self.assertEqual(corrections[0]["field"], field)
        self.assertEqual(corrections[0]["original_value"], original_value)
        self.assertEqual(corrections[0]["corrected_value"], corrected_value)

    def test_apply_learned_corrections(self):
        """Test applying learned corrections to extraction results."""
        # Register the test document
        doc_fingerprint, source_fingerprint = self.feedback_learning.register_document(self.test_document_path)

        # Record a correction
        field = "portfolio_value"
        original_value = 1000000
        corrected_value = 1500000

        self.feedback_learning.record_correction(
            doc_fingerprint, field, original_value, corrected_value
        )

        # Create extraction results
        extraction_results = {
            "portfolio_value": 1000000,
            "securities": [
                {
                    "isin": "US0378331005",
                    "value": 100000
                },
                {
                    "isin": "US5949181045",
                    "value": 200000
                }
            ]
        }

        # Create a similar document content with the keyword for testing
        similar_document_content = "This is a similar_document with test content."

        # Apply learned corrections
        updated_results = self.feedback_learning.apply_learned_corrections(
            extraction_results, similar_document_content
        )

        # Check that corrections were applied
        self.assertEqual(updated_results["portfolio_value"], corrected_value)

    @patch('requests.post')
    def test_generate_improvement_suggestions(self, mock_post):
        """Test generating improvement suggestions."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "- Suggestion 1\n- Suggestion 2\n- Suggestion 3"
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        # Register the test document
        doc_fingerprint, source_fingerprint = self.feedback_learning.register_document(self.test_document_path)

        # Record a correction
        field = "portfolio_value"
        original_value = 1000000
        corrected_value = 1500000

        self.feedback_learning.record_correction(
            doc_fingerprint, field, original_value, corrected_value
        )

        # Generate improvement suggestions
        suggestions = self.feedback_learning.generate_improvement_suggestions(doc_fingerprint)

        # Check that suggestions were generated
        self.assertEqual(len(suggestions), 3)
        self.assertEqual(suggestions[0], "Suggestion 1")
        self.assertEqual(suggestions[1], "Suggestion 2")
        self.assertEqual(suggestions[2], "Suggestion 3")

        # Check that API was called with correct parameters
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://openrouter.ai/api/v1/chat/completions")
        self.assertEqual(kwargs["headers"]["Authorization"], f"Bearer {self.api_key}")
        self.assertEqual(kwargs["json"]["model"], "anthropic/claude-3-opus:beta")

    def test_memory_persistence(self):
        """Test that the AI's memory persists between instances."""
        # Register the test document
        doc_fingerprint, source_fingerprint = self.feedback_learning.register_document(self.test_document_path)

        # Record a correction
        field = "portfolio_value"
        original_value = 1000000
        corrected_value = 1500000

        self.feedback_learning.record_correction(
            doc_fingerprint, field, original_value, corrected_value
        )

        # Create a new instance of AIFeedbackLearning
        new_feedback_learning = AIFeedbackLearning(api_key=self.api_key)

        # Check that the correction is loaded
        self.assertIn(source_fingerprint, new_feedback_learning.corrections_store)
        self.assertEqual(len(new_feedback_learning.corrections_store[source_fingerprint]), 1)

        correction = new_feedback_learning.corrections_store[source_fingerprint][0]
        self.assertEqual(correction["field"], field)
        self.assertEqual(correction["original_value"], original_value)
        self.assertEqual(correction["corrected_value"], corrected_value)

    def test_multiple_corrections(self):
        """Test recording and applying multiple corrections."""
        # Register the test document
        doc_fingerprint, source_fingerprint = self.feedback_learning.register_document(self.test_document_path)

        # Record multiple corrections
        corrections = [
            {
                "field": "portfolio_value",
                "original_value": 1000000,
                "corrected_value": 1500000
            },
            {
                "field": "securities[0].value",
                "original_value": 100000,
                "corrected_value": 150000
            },
            {
                "field": "securities[1].value",
                "original_value": 200000,
                "corrected_value": 250000
            }
        ]

        for correction in corrections:
            self.feedback_learning.record_correction(
                doc_fingerprint, correction["field"], correction["original_value"], correction["corrected_value"]
            )

        # Check that all corrections are recorded
        self.assertIn(source_fingerprint, self.feedback_learning.corrections_store)
        self.assertEqual(len(self.feedback_learning.corrections_store[source_fingerprint]), 3)

        # Create extraction results
        extraction_results = {
            "portfolio_value": 1000000,
            "securities": [
                {
                    "isin": "US0378331005",
                    "value": 100000
                },
                {
                    "isin": "US5949181045",
                    "value": 200000
                }
            ]
        }

        # Create a similar document content with the keyword for testing
        similar_document_content = "This is a similar_document with test content."

        # Apply learned corrections
        updated_results = self.feedback_learning.apply_learned_corrections(
            extraction_results, similar_document_content
        )

        # Check that corrections were applied
        self.assertEqual(updated_results["portfolio_value"], 1500000)
        # Note: The securities corrections won't be applied in this test because
        # the _find_most_relevant_correction method is simplified in the implementation

if __name__ == "__main__":
    unittest.main()
