"""
Financial Q&A Robot - Answers questions about financial documents.
"""
import os
import sys
import json
import re
import random
from enhanced_financial_extractor import EnhancedFinancialExtractor

class FinancialQARobot:
    """Robot that answers questions about financial documents."""

    def __init__(self):
        self.extractor = EnhancedFinancialExtractor()
        self.portfolio_value = None
        self.securities = []
        self.asset_classes = {}
        self.questions = [
            "What is the total portfolio value?",
            "How many securities are in the portfolio?",
            "What are the main asset classes in the portfolio?",
            "What is the largest security in the portfolio?",
            "What are the top 5 holdings in the portfolio?",
            "What is the percentage allocation to bonds?",
            "What is the percentage allocation to equities?",
            "What is the total value of bonds in the portfolio?",
            "What is the total value of equities in the portfolio?",
            "What is the average price of securities in the portfolio?",
            "What is the discrepancy between portfolio value and sum of securities?"
        ]

    def process_document(self, pdf_path):
        """Process a financial document and prepare for Q&A."""
        print(f"Processing document: {pdf_path}")

        # Process the document with the enhanced financial extractor
        self.extractor.process(pdf_path)

        # Get the extracted data
        self.portfolio_value = self.extractor.portfolio_value
        self.securities = self.extractor.securities
        self.asset_classes = self.extractor.asset_classes

        print("Document processed. Ready for Q&A.")
        print(f"Portfolio Value: ${self.portfolio_value:,.2f}" if self.portfolio_value else "Portfolio Value not found")
        print(f"Securities found: {len(self.securities)}")
        print(f"Asset Classes: {', '.join(self.asset_classes.keys())}")

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
        if not self.portfolio_value and not self.securities:
            return "I don't have enough data to answer questions. Please process a document first."

        # Portfolio value questions
        if re.search(r'(portfolio|total).*value', question_lower) or re.search(r'value.*(portfolio|total)', question_lower):
            if self.portfolio_value:
                return f"The total portfolio value is ${self.portfolio_value:,.2f}."
            else:
                return "I couldn't find the portfolio value in the document."

        # Number of securities questions
        elif re.search(r'how many (securities|stocks|bonds|holdings)', question_lower) or re.search(r'number of (securities|stocks|bonds|holdings)', question_lower):
            return f"There are {len(self.securities)} securities in the portfolio."

        # Asset classes questions
        elif re.search(r'asset (classes|allocation)', question_lower) or re.search(r'(classes|types) of assets', question_lower):
            asset_classes = list(self.asset_classes.keys())
            if asset_classes:
                return f"The main asset classes in the portfolio are: {', '.join(asset_classes)}."
            else:
                return "I couldn't find information about asset classes in the document."

        # Largest security questions
        elif re.search(r'largest (security|holding|position)', question_lower) or re.search(r'biggest (security|holding|position)', question_lower):
            securities_with_value = [s for s in self.securities if s.get('value')]
            if securities_with_value:
                largest = max(securities_with_value, key=lambda s: s.get('value', 0))
                return f"The largest security is {largest.get('name', largest.get('isin', 'Unknown'))} with a value of ${largest.get('value', 0):,.2f}."
            else:
                return "I couldn't determine the largest security because value information is missing."

        # Top holdings questions
        elif re.search(r'top \d+ (holdings|securities|positions)', question_lower):
            # Extract the number from the question (default to 5 if not found)
            match = re.search(r'top (\d+)', question_lower)
            num_holdings = int(match.group(1)) if match else 5

            securities_with_value = [s for s in self.securities if s.get('value')]
            if securities_with_value:
                # Sort securities by value (descending)
                top_securities = sorted(securities_with_value, key=lambda s: s.get('value', 0), reverse=True)[:num_holdings]

                # Calculate total portfolio value from securities
                total_value = sum(s.get('value', 0) for s in securities_with_value)

                # Format the response
                response = f"The top {len(top_securities)} holdings are:\n"
                for i, security in enumerate(top_securities, 1):
                    name = security.get('name', security.get('isin', 'Unknown'))
                    value = security.get('value', 0)
                    percentage = (value / total_value * 100) if total_value > 0 else 0
                    response += f"{i}. {name}: ${value:,.2f} ({percentage:.2f}% of portfolio)\n"

                return response
            else:
                return "I couldn't determine the top holdings because value information is missing."

        # Bond allocation questions
        elif re.search(r'(percentage|allocation|percent).*bonds', question_lower) or re.search(r'bonds.*(percentage|allocation|percent)', question_lower):
            if 'Bonds' in self.asset_classes:
                total_value = sum(data['total_value'] for data in self.asset_classes.values())
                bonds_value = self.asset_classes['Bonds']['total_value']
                if total_value > 0:
                    percentage = (bonds_value / total_value) * 100
                    return f"The allocation to bonds is {percentage:.2f}% of the portfolio."
                else:
                    return "I couldn't calculate the percentage allocation to bonds because the total portfolio value is zero or missing."
            else:
                return "I couldn't find information about bonds in the portfolio."

        # Equity allocation questions
        elif re.search(r'(percentage|allocation|percent).*equities', question_lower) or re.search(r'equities.*(percentage|allocation|percent)', question_lower):
            if 'Equities' in self.asset_classes:
                total_value = sum(data['total_value'] for data in self.asset_classes.values())
                equities_value = self.asset_classes['Equities']['total_value']
                if total_value > 0:
                    percentage = (equities_value / total_value) * 100
                    return f"The allocation to equities is {percentage:.2f}% of the portfolio."
                else:
                    return "I couldn't calculate the percentage allocation to equities because the total portfolio value is zero or missing."
            else:
                return "I couldn't find information about equities in the portfolio."

        # Bond value questions
        elif re.search(r'(value|total).*bonds', question_lower) or re.search(r'bonds.*(value|total)', question_lower):
            if 'Bonds' in self.asset_classes:
                bonds_value = self.asset_classes['Bonds']['total_value']
                return f"The total value of bonds in the portfolio is ${bonds_value:,.2f}."
            else:
                return "I couldn't find information about bonds in the portfolio."

        # Equity value questions
        elif re.search(r'(value|total).*equities', question_lower) or re.search(r'equities.*(value|total)', question_lower):
            if 'Equities' in self.asset_classes:
                equities_value = self.asset_classes['Equities']['total_value']
                return f"The total value of equities in the portfolio is ${equities_value:,.2f}."
            else:
                return "I couldn't find information about equities in the portfolio."

        # Average price questions
        elif re.search(r'average (price|cost)', question_lower):
            securities_with_price = [s for s in self.securities if s.get('price')]
            if securities_with_price:
                avg_price = sum(s.get('price', 0) for s in securities_with_price) / len(securities_with_price)
                return f"The average price of securities in the portfolio is ${avg_price:,.2f}."
            else:
                return "I couldn't calculate the average price because price information is missing."

        # Discrepancy questions
        elif re.search(r'(discrepancy|difference)', question_lower):
            total_securities_value = sum(s.get('value', 0) for s in self.securities if s.get('value'))
            if self.portfolio_value and total_securities_value:
                discrepancy = self.portfolio_value - total_securities_value
                discrepancy_pct = (discrepancy / self.portfolio_value) * 100
                return f"The discrepancy between portfolio value (${self.portfolio_value:,.2f}) and sum of securities (${total_securities_value:,.2f}) is ${discrepancy:,.2f} ({discrepancy_pct:.2f}%)."
            else:
                return "I couldn't calculate the discrepancy because either portfolio value or securities values are missing."

        # Generic fallback
        else:
            return "I'm not sure how to answer that question. Please try asking about portfolio value, securities, asset classes, or allocation percentages."

    def generate_random_question(self):
        """Generate a random question from the predefined list."""
        return random.choice(self.questions)

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python financial_qa_robot.py <pdf_path>")
        return 1

    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        return 1

    robot = FinancialQARobot()
    robot.process_document(pdf_path)
    robot.start_interactive_session()

    return 0

if __name__ == "__main__":
    sys.exit(main())
