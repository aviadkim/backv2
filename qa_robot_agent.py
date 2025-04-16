"""
Q&A Robot Agent - Answers questions about financial documents.
"""
import os
import json
import re
import random
from datetime import datetime

class QARobotAgent:
    """Agent that answers questions about financial documents."""
    
    def __init__(self):
        self.document_structure = None
        self.financial_values = None
        self.securities = None
        self.validation_results = None
        self.ocr_results = None
        self.questions = [
            "What is the total portfolio value?",
            "How many securities are in the portfolio?",
            "What are the main asset classes in the portfolio?",
            "What is the largest security in the portfolio?",
            "What is the date of the document?",
            "What is the currency used in the document?",
            "What is the percentage allocation to bonds?",
            "Are there any validation issues with the data?",
            "What is the confidence level of the extracted data?",
            "What is the total value of equities in the portfolio?"
        ]
    
    def load_data(self, data_dir):
        """Load data from the specified directory."""
        print(f"Loading data from {data_dir}...")
        
        # Load document structure
        try:
            with open(os.path.join(data_dir, 'document_structure.json'), 'r', encoding='utf-8') as f:
                self.document_structure = json.load(f)
            print("Loaded document structure")
        except Exception as e:
            print(f"Error loading document structure: {str(e)}")
        
        # Load financial values
        try:
            with open(os.path.join(data_dir, 'financial_values.json'), 'r', encoding='utf-8') as f:
                self.financial_values = json.load(f)
            print("Loaded financial values")
        except Exception as e:
            print(f"Error loading financial values: {str(e)}")
        
        # Load securities
        try:
            with open(os.path.join(data_dir, 'securities.json'), 'r', encoding='utf-8') as f:
                self.securities = json.load(f)
            print("Loaded securities")
        except Exception as e:
            print(f"Error loading securities: {str(e)}")
        
        # Load validation results
        try:
            with open(os.path.join(data_dir, 'validation_results.json'), 'r', encoding='utf-8') as f:
                self.validation_results = json.load(f)
            print("Loaded validation results")
        except Exception as e:
            print(f"Error loading validation results: {str(e)}")
        
        # Load OCR results
        try:
            with open(os.path.join(data_dir, 'ocr_results.json'), 'r', encoding='utf-8') as f:
                self.ocr_results = json.load(f)
            print("Loaded OCR results")
        except Exception as e:
            print(f"Error loading OCR results: {str(e)}")
    
    def start_interactive_session(self):
        """Start an interactive Q&A session."""
        print("\nFinancial Document Q&A Robot")
        print("============================")
        print("I can answer questions about the financial document.")
        print("Type 'exit' to end the session.")
        print("Type 'auto' to see answers to 10 common questions.")
        print()
        
        while True:
            user_input = input("Ask a question: ").strip()
            
            if user_input.lower() == 'exit':
                print("Ending Q&A session. Goodbye!")
                break
            
            elif user_input.lower() == 'auto':
                self._run_auto_mode()
                continue
            
            answer = self.answer_question(user_input)
            print(f"Answer: {answer}\n")
    
    def _run_auto_mode(self):
        """Run automatic Q&A mode with predefined questions."""
        print("\nAutomatic Q&A Mode")
        print("==================")
        
        for i, question in enumerate(self.questions, 1):
            print(f"\nQuestion {i}: {question}")
            answer = self.answer_question(question)
            print(f"Answer: {answer}")
            
            # Pause between questions
            if i < len(self.questions):
                input("Press Enter for next question...")
        
        print("\nAutomatic Q&A completed.")
    
    def answer_question(self, question):
        """Answer a question about the financial document."""
        question_lower = question.lower()
        
        # Check if we have the necessary data
        if not any([self.document_structure, self.financial_values, self.securities, self.validation_results]):
            return "I don't have enough data to answer questions. Please process a document first."
        
        # Portfolio value questions
        if re.search(r'(portfolio|total).*value', question_lower) or re.search(r'value.*(portfolio|total)', question_lower):
            if self.financial_values and 'portfolio_value' in self.financial_values:
                portfolio_value = self.financial_values['portfolio_value']
                return f"The total portfolio value is ${portfolio_value:,.2f}."
            else:
                return "I couldn't find the portfolio value in the document."
        
        # Number of securities questions
        elif re.search(r'how many (securities|stocks|bonds|holdings)', question_lower) or re.search(r'number of (securities|stocks|bonds|holdings)', question_lower):
            if self.securities and 'securities' in self.securities:
                num_securities = len(self.securities['securities'])
                return f"There are {num_securities} securities in the portfolio."
            else:
                return "I couldn't find information about securities in the document."
        
        # Asset classes questions
        elif re.search(r'asset (classes|allocation)', question_lower) or re.search(r'(classes|types) of assets', question_lower):
            if self.securities and 'asset_classes' in self.securities:
                asset_classes = list(self.securities['asset_classes'].keys())
                if asset_classes:
                    return f"The main asset classes in the portfolio are: {', '.join(asset_classes)}."
                else:
                    return "I couldn't find information about asset classes in the document."
            else:
                return "I couldn't find information about asset classes in the document."
        
        # Largest security questions
        elif re.search(r'largest (security|holding|position)', question_lower) or re.search(r'biggest (security|holding|position)', question_lower):
            if self.securities and 'securities' in self.securities:
                securities = self.securities['securities']
                if securities:
                    # Sort by value
                    securities_with_value = [s for s in securities if s.get('value')]
                    if securities_with_value:
                        largest = max(securities_with_value, key=lambda s: s.get('value', 0))
                        return f"The largest security is {largest.get('name', largest.get('isin', 'Unknown'))} with a value of ${largest.get('value', 0):,.2f}."
                    else:
                        return "I couldn't determine the largest security because value information is missing."
                else:
                    return "I couldn't find information about securities in the document."
            else:
                return "I couldn't find information about securities in the document."
        
        # Document date questions
        elif re.search(r'(date|when)', question_lower):
            if self.document_structure and 'document_date' in self.document_structure:
                document_date = self.document_structure['document_date']
                return f"The document date is {document_date}."
            else:
                return "I couldn't find the document date."
        
        # Currency questions
        elif re.search(r'currency', question_lower):
            if self.financial_values and 'currency' in self.financial_values:
                currency = self.financial_values['currency']
                return f"The currency used in the document is {currency}."
            else:
                return "I couldn't determine the currency used in the document."
        
        # Asset allocation percentage questions
        elif re.search(r'(percentage|allocation|percent).*bonds', question_lower) or re.search(r'bonds.*(percentage|allocation|percent)', question_lower):
            if self.securities and 'asset_classes' in self.securities:
                asset_classes = self.securities['asset_classes']
                total_value = sum(data.get('total_value', 0) for data in asset_classes.values())
                
                if 'Bonds' in asset_classes:
                    bonds_value = asset_classes['Bonds'].get('total_value', 0)
                    if total_value > 0:
                        percentage = (bonds_value / total_value) * 100
                        return f"The allocation to bonds is {percentage:.2f}% of the portfolio."
                    else:
                        return "I couldn't calculate the percentage allocation to bonds because the total portfolio value is zero or missing."
                else:
                    return "I couldn't find information about bonds in the portfolio."
            else:
                return "I couldn't find information about asset allocation in the document."
        
        # Validation issues questions
        elif re.search(r'(validation|issues|problems|errors)', question_lower):
            if self.validation_results and 'issues' in self.validation_results:
                issues = self.validation_results['issues']
                if issues:
                    num_issues = len(issues)
                    issue_types = set(issue['type'] for issue in issues)
                    return f"There are {num_issues} validation issues: {', '.join(issue_types)}."
                else:
                    return "No validation issues were found in the document."
            else:
                return "I couldn't find information about validation issues."
        
        # Confidence level questions
        elif re.search(r'(confidence|accuracy|reliability)', question_lower):
            if self.validation_results and 'confidence_scores' in self.validation_results:
                confidence_scores = self.validation_results['confidence_scores']
                if 'overall' in confidence_scores:
                    overall = confidence_scores['overall'] * 100
                    return f"The overall confidence level of the extracted data is {overall:.2f}%."
                else:
                    return "I couldn't find an overall confidence score for the extracted data."
            else:
                return "I couldn't find information about confidence scores."
        
        # Equities value questions
        elif re.search(r'(value|total).*equities', question_lower) or re.search(r'equities.*(value|total)', question_lower):
            if self.securities and 'asset_classes' in self.securities:
                asset_classes = self.securities['asset_classes']
                if 'Equities' in asset_classes:
                    equities_value = asset_classes['Equities'].get('total_value', 0)
                    return f"The total value of equities in the portfolio is ${equities_value:,.2f}."
                else:
                    return "I couldn't find information about equities in the portfolio."
            else:
                return "I couldn't find information about asset classes in the document."
        
        # Generic fallback
        else:
            return "I'm not sure how to answer that question. Please try asking about portfolio value, securities, asset classes, document date, or validation issues."
    
    def generate_random_question(self):
        """Generate a random question from the predefined list."""
        return random.choice(self.questions)

if __name__ == "__main__":
    agent = QARobotAgent()
    agent.load_data('agent_results')
    agent.start_interactive_session()
