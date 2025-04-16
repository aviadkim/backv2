"""
Financial Agent - Answers questions about financial documents.
"""
import os
import re
import json
import pandas as pd
from typing import Dict, List, Any, Optional
from financial_document_processor import FinancialDocumentProcessor

class FinancialAgent:
    """
    Agent that answers questions about financial documents.
    """
    
    def __init__(self):
        """Initialize the financial agent."""
        self.processor = FinancialDocumentProcessor()
        self.documents = {}  # Store processed documents by path
    
    def load_document(self, pdf_path: str, output_dir: Optional[str] = None) -> bool:
        """
        Load and process a financial document.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save output files (default: None)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"Loading document: {pdf_path}")
            
            # Process the document
            extracted_data = self.processor.process(pdf_path, output_dir=output_dir)
            
            # Store the document
            self.documents[pdf_path] = {
                "extracted_data": extracted_data,
                "full_text": self.processor.full_text
            }
            
            print(f"Document loaded successfully: {pdf_path}")
            return True
            
        except Exception as e:
            print(f"Error loading document: {str(e)}")
            return False
    
    def answer_question(self, question: str, pdf_path: Optional[str] = None) -> str:
        """
        Answer a question about a financial document.
        
        Args:
            question: Question to answer
            pdf_path: Path to the specific document to query (default: None, uses the last loaded document)
        
        Returns:
            Answer to the question
        """
        # If no document is specified, use the last loaded document
        if pdf_path is None:
            if not self.documents:
                return "Please load a document first."
            pdf_path = list(self.documents.keys())[-1]
        
        # Check if the document is loaded
        if pdf_path not in self.documents:
            return f"Document not loaded: {pdf_path}"
        
        # Use the processor to answer the question
        return self.processor.answer_question(question)
    
    def generate_report(self, pdf_path: Optional[str] = None, output_dir: Optional[str] = None) -> str:
        """
        Generate a report for a financial document.
        
        Args:
            pdf_path: Path to the specific document to generate a report for (default: None, uses the last loaded document)
            output_dir: Directory to save the report (default: None)
        
        Returns:
            Path to the generated report
        """
        # If no document is specified, use the last loaded document
        if pdf_path is None:
            if not self.documents:
                print("Please load a document first.")
                return ""
            pdf_path = list(self.documents.keys())[-1]
        
        # Check if the document is loaded
        if pdf_path not in self.documents:
            print(f"Document not loaded: {pdf_path}")
            return ""
        
        # Generate the report
        return self.processor.generate_report(output_dir=output_dir)
    
    def start_interactive_session(self):
        """Start an interactive Q&A session."""
        if not self.documents:
            print("Please load a document first.")
            return
        
        print("\nFinancial Agent")
        print("==============")
        print("I can answer questions about financial documents.")
        print("Type 'exit' to end the session.")
        print("Type 'help' to see example questions.")
        print("Type 'report' to generate a report.")
        print("Type 'load <pdf_path>' to load a different document.")
        print()
        
        while True:
            user_input = input("Ask a question: ").strip()
            
            if user_input.lower() == 'exit':
                print("Ending session. Goodbye!")
                break
            
            elif user_input.lower() == 'help':
                print("\nExample questions:")
                print("- What is the total portfolio value?")
                print("- What is the asset allocation?")
                print("- What are the top 5 holdings?")
                print("- What are the top 10 bonds?")
                print("- What is the client information?")
                print("- What is the document date?")
                print()
                continue
            
            elif user_input.lower() == 'report':
                report_path = self.generate_report()
                if report_path:
                    print(f"Report generated: {report_path}")
                    # Open the report in the default browser
                    import webbrowser
                    webbrowser.open(f"file://{os.path.abspath(report_path)}")
                continue
            
            elif user_input.lower().startswith('load '):
                # Extract the PDF path
                pdf_path = user_input[5:].strip()
                if os.path.exists(pdf_path):
                    self.load_document(pdf_path)
                else:
                    print(f"File not found: {pdf_path}")
                continue
            
            answer = self.answer_question(user_input)
            print(f"\n{answer}\n")

def main():
    """Main function."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Financial Agent")
    parser.add_argument("file_path", help="Path to the financial document")
    parser.add_argument("--output-dir", help="Directory to save output files")
    parser.add_argument("--question", help="Question to answer (if provided, skips interactive mode)")
    parser.add_argument("--report", action="store_true", help="Generate a report")
    
    args = parser.parse_args()
    
    # Check if the file exists
    if not os.path.exists(args.file_path):
        print(f"Error: File not found: {args.file_path}")
        return 1
    
    # Create the agent
    agent = FinancialAgent()
    
    # Load the document
    if not agent.load_document(args.file_path, output_dir=args.output_dir):
        print(f"Error loading document: {args.file_path}")
        return 1
    
    # Generate a report if requested
    if args.report:
        report_path = agent.generate_report(output_dir=args.output_dir)
        if report_path:
            print(f"Report generated: {report_path}")
            # Open the report in the default browser
            import webbrowser
            webbrowser.open(f"file://{os.path.abspath(report_path)}")
    
    # Answer a specific question if provided
    if args.question:
        answer = agent.answer_question(args.question)
        print(f"\nQuestion: {args.question}")
        print(f"Answer: {answer}\n")
    # Otherwise, start interactive session
    else:
        agent.start_interactive_session()
    
    return 0

if __name__ == "__main__":
    main()
