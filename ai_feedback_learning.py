"""
AI Feedback Learning - Implements a feedback mechanism for the AI to learn from corrections.

This module provides tools to collect user feedback on extraction results and
use that feedback to improve future extractions from similar documents.
"""
import os
import json
import logging
import hashlib
from typing import Dict, List, Any, Optional, Tuple
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIFeedbackLearning:
    """
    Implements a feedback mechanism for the AI to learn from corrections.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the AI feedback learning module.
        
        Args:
            api_key: OpenRouter API key (default: None, will try to get from environment)
        """
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            logger.warning("No OpenRouter API key provided. AI learning capabilities will be limited.")
        
        self.feedback_store = {}
        self.corrections_store = {}
        self.document_fingerprints = {}
        
        # Load existing feedback and corrections if available
        self._load_feedback_store()
        self._load_corrections_store()
    
    def _load_feedback_store(self):
        """Load existing feedback store from file."""
        try:
            if os.path.exists("feedback_store.json"):
                with open("feedback_store.json", "r", encoding="utf-8") as f:
                    self.feedback_store = json.load(f)
                logger.info(f"Loaded {len(self.feedback_store)} feedback entries")
        except Exception as e:
            logger.error(f"Error loading feedback store: {str(e)}")
    
    def _load_corrections_store(self):
        """Load existing corrections store from file."""
        try:
            if os.path.exists("corrections_store.json"):
                with open("corrections_store.json", "r", encoding="utf-8") as f:
                    self.corrections_store = json.load(f)
                logger.info(f"Loaded {len(self.corrections_store)} correction entries")
        except Exception as e:
            logger.error(f"Error loading corrections store: {str(e)}")
    
    def _save_feedback_store(self):
        """Save feedback store to file."""
        try:
            with open("feedback_store.json", "w", encoding="utf-8") as f:
                json.dump(self.feedback_store, f, indent=2)
            logger.info(f"Saved {len(self.feedback_store)} feedback entries")
        except Exception as e:
            logger.error(f"Error saving feedback store: {str(e)}")
    
    def _save_corrections_store(self):
        """Save corrections store to file."""
        try:
            with open("corrections_store.json", "w", encoding="utf-8") as f:
                json.dump(self.corrections_store, f, indent=2)
            logger.info(f"Saved {len(self.corrections_store)} correction entries")
        except Exception as e:
            logger.error(f"Error saving corrections store: {str(e)}")
    
    def _compute_document_fingerprint(self, document_content: str) -> str:
        """
        Compute a fingerprint for a document based on its content.
        
        Args:
            document_content: Content of the document
        
        Returns:
            Document fingerprint
        """
        # Create a hash of the document content
        return hashlib.md5(document_content.encode("utf-8")).hexdigest()
    
    def _compute_document_source_fingerprint(self, document_content: str) -> str:
        """
        Compute a fingerprint for the document source based on patterns in the content.
        
        Args:
            document_content: Content of the document
        
        Returns:
            Document source fingerprint
        """
        # Extract key patterns that identify the document source
        # This is a simplified implementation - in a real system, you would use more sophisticated
        # techniques to identify the document source
        
        # Look for headers, footers, logos, etc.
        lines = document_content.split("\n")
        header_lines = lines[:10]
        footer_lines = lines[-10:]
        
        # Combine header and footer to create a source fingerprint
        source_content = "\n".join(header_lines + footer_lines)
        return hashlib.md5(source_content.encode("utf-8")).hexdigest()
    
    def register_document(self, document_path: str) -> Tuple[str, str]:
        """
        Register a document for feedback learning.
        
        Args:
            document_path: Path to the document
        
        Returns:
            Tuple of document fingerprint and source fingerprint
        """
        try:
            # Read document content
            with open(document_path, "rb") as f:
                document_content = f.read().decode("utf-8", errors="ignore")
            
            # Compute fingerprints
            doc_fingerprint = self._compute_document_fingerprint(document_content)
            source_fingerprint = self._compute_document_source_fingerprint(document_content)
            
            # Store fingerprints
            self.document_fingerprints[doc_fingerprint] = {
                "source_fingerprint": source_fingerprint,
                "document_path": document_path,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Registered document {document_path} with fingerprint {doc_fingerprint}")
            return doc_fingerprint, source_fingerprint
        
        except Exception as e:
            logger.error(f"Error registering document: {str(e)}")
            return None, None
    
    def record_feedback(self, document_fingerprint: str, extraction_results: Dict[str, Any], 
                        feedback: Dict[str, Any]) -> bool:
        """
        Record user feedback on extraction results.
        
        Args:
            document_fingerprint: Fingerprint of the document
            extraction_results: Original extraction results
            feedback: User feedback on the extraction results
        
        Returns:
            True if feedback was successfully recorded, False otherwise
        """
        try:
            if document_fingerprint not in self.document_fingerprints:
                logger.warning(f"Document with fingerprint {document_fingerprint} not registered")
                return False
            
            source_fingerprint = self.document_fingerprints[document_fingerprint]["source_fingerprint"]
            
            # Create feedback entry
            feedback_entry = {
                "document_fingerprint": document_fingerprint,
                "source_fingerprint": source_fingerprint,
                "extraction_results": extraction_results,
                "feedback": feedback,
                "timestamp": datetime.now().isoformat()
            }
            
            # Store feedback
            if source_fingerprint not in self.feedback_store:
                self.feedback_store[source_fingerprint] = []
            
            self.feedback_store[source_fingerprint].append(feedback_entry)
            
            # Save feedback store
            self._save_feedback_store()
            
            logger.info(f"Recorded feedback for document {document_fingerprint}")
            return True
        
        except Exception as e:
            logger.error(f"Error recording feedback: {str(e)}")
            return False
    
    def record_correction(self, document_fingerprint: str, field: str, 
                         original_value: Any, corrected_value: Any) -> bool:
        """
        Record a correction made by the user.
        
        Args:
            document_fingerprint: Fingerprint of the document
            field: Field that was corrected
            original_value: Original value
            corrected_value: Corrected value
        
        Returns:
            True if correction was successfully recorded, False otherwise
        """
        try:
            if document_fingerprint not in self.document_fingerprints:
                logger.warning(f"Document with fingerprint {document_fingerprint} not registered")
                return False
            
            source_fingerprint = self.document_fingerprints[document_fingerprint]["source_fingerprint"]
            
            # Create correction entry
            correction_entry = {
                "document_fingerprint": document_fingerprint,
                "source_fingerprint": source_fingerprint,
                "field": field,
                "original_value": original_value,
                "corrected_value": corrected_value,
                "timestamp": datetime.now().isoformat()
            }
            
            # Store correction
            if source_fingerprint not in self.corrections_store:
                self.corrections_store[source_fingerprint] = []
            
            self.corrections_store[source_fingerprint].append(correction_entry)
            
            # Save corrections store
            self._save_corrections_store()
            
            # Learn from correction using AI
            self._learn_from_correction(correction_entry)
            
            logger.info(f"Recorded correction for document {document_fingerprint}, field {field}")
            return True
        
        except Exception as e:
            logger.error(f"Error recording correction: {str(e)}")
            return False
    
    def _learn_from_correction(self, correction_entry: Dict[str, Any]) -> bool:
        """
        Learn from a correction using AI.
        
        Args:
            correction_entry: Correction entry
        
        Returns:
            True if learning was successful, False otherwise
        """
        if not self.api_key:
            logger.warning("No OpenRouter API key provided. Cannot learn from correction.")
            return False
        
        try:
            # Prepare message for AI
            message = {
                "role": "system",
                "content": "You are an AI assistant that helps improve document extraction. "
                           "Learn from the correction and provide insights on how to improve future extractions."
            }
            
            user_message = {
                "role": "user",
                "content": f"I extracted '{correction_entry['original_value']}' for the field '{correction_entry['field']}', "
                           f"but the correct value is '{correction_entry['corrected_value']}'. "
                           f"What pattern can you identify to improve future extractions for this field?"
            }
            
            # Call OpenRouter API
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "anthropic/claude-3-opus:beta",  # Using Claude 3 Opus for best reasoning
                    "messages": [message, user_message]
                }
            )
            
            if response.status_code == 200:
                ai_response = response.json()
                
                # Extract insights from AI response
                insights = ai_response["choices"][0]["message"]["content"]
                
                # Store insights with correction
                correction_entry["ai_insights"] = insights
                self._save_corrections_store()
                
                logger.info(f"Learned from correction for field {correction_entry['field']}")
                return True
            else:
                logger.error(f"Error calling OpenRouter API: {response.status_code} - {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"Error learning from correction: {str(e)}")
            return False
    
    def get_similar_document_corrections(self, document_content: str) -> List[Dict[str, Any]]:
        """
        Get corrections for similar documents.
        
        Args:
            document_content: Content of the document
        
        Returns:
            List of corrections for similar documents
        """
        try:
            # Compute source fingerprint
            source_fingerprint = self._compute_document_source_fingerprint(document_content)
            
            # Get corrections for this source
            if source_fingerprint in self.corrections_store:
                return self.corrections_store[source_fingerprint]
            
            return []
        
        except Exception as e:
            logger.error(f"Error getting similar document corrections: {str(e)}")
            return []
    
    def apply_learned_corrections(self, extraction_results: Dict[str, Any], document_content: str) -> Dict[str, Any]:
        """
        Apply learned corrections to extraction results.
        
        Args:
            extraction_results: Extraction results
            document_content: Content of the document
        
        Returns:
            Updated extraction results
        """
        try:
            # Get corrections for similar documents
            similar_corrections = self.get_similar_document_corrections(document_content)
            
            if not similar_corrections:
                logger.info("No similar document corrections found")
                return extraction_results
            
            # Create a copy of extraction results
            updated_results = dict(extraction_results)
            
            # Group corrections by field
            corrections_by_field = {}
            for correction in similar_corrections:
                field = correction["field"]
                if field not in corrections_by_field:
                    corrections_by_field[field] = []
                corrections_by_field[field].append(correction)
            
            # Apply corrections
            for field, corrections in corrections_by_field.items():
                # Check if field exists in extraction results
                if field not in updated_results:
                    continue
                
                # Get original value
                original_value = updated_results[field]
                
                # Find most relevant correction
                most_relevant_correction = self._find_most_relevant_correction(original_value, corrections)
                
                if most_relevant_correction:
                    # Apply correction
                    if isinstance(original_value, dict) and "value" in original_value:
                        # If the field is a dictionary with a value key
                        updated_results[field]["value"] = most_relevant_correction["corrected_value"]
                        updated_results[field]["corrected"] = True
                        updated_results[field]["original_value"] = original_value["value"]
                    else:
                        # If the field is a simple value
                        updated_results[field] = most_relevant_correction["corrected_value"]
            
            logger.info(f"Applied learned corrections to extraction results")
            return updated_results
        
        except Exception as e:
            logger.error(f"Error applying learned corrections: {str(e)}")
            return extraction_results
    
    def _find_most_relevant_correction(self, original_value: Any, corrections: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Find the most relevant correction for a value.
        
        Args:
            original_value: Original value
            corrections: List of corrections
        
        Returns:
            Most relevant correction or None if no relevant correction found
        """
        # This is a simplified implementation - in a real system, you would use more sophisticated
        # techniques to find the most relevant correction
        
        # Convert original value to string for comparison
        if isinstance(original_value, dict) and "value" in original_value:
            original_str = str(original_value["value"])
        else:
            original_str = str(original_value)
        
        # Find correction with most similar original value
        most_similar_correction = None
        highest_similarity = 0
        
        for correction in corrections:
            correction_original = str(correction["original_value"])
            
            # Calculate similarity (simple implementation)
            similarity = self._calculate_similarity(original_str, correction_original)
            
            if similarity > highest_similarity:
                highest_similarity = similarity
                most_similar_correction = correction
        
        # Only return correction if similarity is above threshold
        if highest_similarity > 0.7:
            return most_similar_correction
        
        return None
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings.
        
        Args:
            str1: First string
            str2: Second string
        
        Returns:
            Similarity score between 0 and 1
        """
        # This is a simplified implementation - in a real system, you would use more sophisticated
        # techniques to calculate similarity
        
        # Convert to lowercase
        str1 = str1.lower()
        str2 = str2.lower()
        
        # Calculate Jaccard similarity
        set1 = set(str1)
        set2 = set(str2)
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        if union == 0:
            return 0
        
        return intersection / union
    
    def generate_improvement_suggestions(self, document_fingerprint: str) -> List[str]:
        """
        Generate suggestions for improving extraction based on corrections.
        
        Args:
            document_fingerprint: Fingerprint of the document
        
        Returns:
            List of improvement suggestions
        """
        if not self.api_key:
            logger.warning("No OpenRouter API key provided. Cannot generate improvement suggestions.")
            return ["API key required for generating improvement suggestions."]
        
        try:
            if document_fingerprint not in self.document_fingerprints:
                logger.warning(f"Document with fingerprint {document_fingerprint} not registered")
                return ["Document not registered for feedback learning."]
            
            source_fingerprint = self.document_fingerprints[document_fingerprint]["source_fingerprint"]
            
            # Get corrections for this source
            if source_fingerprint not in self.corrections_store:
                return ["No corrections available for this document source."]
            
            corrections = self.corrections_store[source_fingerprint]
            
            # Prepare message for AI
            message = {
                "role": "system",
                "content": "You are an AI assistant that helps improve document extraction. "
                           "Analyze the corrections and provide suggestions for improving future extractions."
            }
            
            corrections_text = json.dumps(corrections, indent=2)
            user_message = {
                "role": "user",
                "content": f"Here are the corrections made for documents from this source:\n\n{corrections_text}\n\n"
                           f"Based on these corrections, what suggestions do you have for improving future extractions?"
            }
            
            # Call OpenRouter API
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "anthropic/claude-3-opus:beta",  # Using Claude 3 Opus for best reasoning
                    "messages": [message, user_message]
                }
            )
            
            if response.status_code == 200:
                ai_response = response.json()
                
                # Extract suggestions from AI response
                suggestions_text = ai_response["choices"][0]["message"]["content"]
                
                # Parse suggestions into a list
                suggestions = []
                for line in suggestions_text.split("\n"):
                    line = line.strip()
                    if line.startswith("- ") or line.startswith("* "):
                        suggestions.append(line[2:])
                    elif line.startswith("1. ") or line.startswith("2. ") or line.startswith("3. "):
                        suggestions.append(line[3:])
                
                if not suggestions:
                    suggestions = [suggestions_text]
                
                return suggestions
            else:
                logger.error(f"Error calling OpenRouter API: {response.status_code} - {response.text}")
                return ["Error generating improvement suggestions."]
        
        except Exception as e:
            logger.error(f"Error generating improvement suggestions: {str(e)}")
            return [f"Error: {str(e)}"]

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Feedback Learning for Document Extraction")
    parser.add_argument("--api-key", help="OpenRouter API key")
    parser.add_argument("--document", help="Path to the document")
    parser.add_argument("--register", action="store_true", help="Register the document")
    parser.add_argument("--correct", action="store_true", help="Record a correction")
    parser.add_argument("--field", help="Field to correct")
    parser.add_argument("--original", help="Original value")
    parser.add_argument("--corrected", help="Corrected value")
    parser.add_argument("--suggestions", action="store_true", help="Generate improvement suggestions")
    
    args = parser.parse_args()
    
    # Initialize AI feedback learning
    feedback_learning = AIFeedbackLearning(api_key=args.api_key)
    
    if args.register and args.document:
        # Register document
        doc_fingerprint, source_fingerprint = feedback_learning.register_document(args.document)
        print(f"Document registered with fingerprint: {doc_fingerprint}")
        print(f"Source fingerprint: {source_fingerprint}")
    
    elif args.correct and args.document and args.field and args.original and args.corrected:
        # Register document if not already registered
        doc_fingerprint, _ = feedback_learning.register_document(args.document)
        
        # Record correction
        success = feedback_learning.record_correction(
            doc_fingerprint, args.field, args.original, args.corrected
        )
        
        if success:
            print(f"Correction recorded for field: {args.field}")
        else:
            print("Failed to record correction")
    
    elif args.suggestions and args.document:
        # Register document if not already registered
        doc_fingerprint, _ = feedback_learning.register_document(args.document)
        
        # Generate improvement suggestions
        suggestions = feedback_learning.generate_improvement_suggestions(doc_fingerprint)
        
        print("Improvement Suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
