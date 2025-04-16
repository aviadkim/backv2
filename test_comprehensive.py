"""
Comprehensive test script for financial document processing.
"""
import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to import required libraries
try:
    import pdfplumber
    import unstructured
    from unstructured.partition.pdf import partition_pdf
    import camelot
    import openai
    from langchain.llms import OpenAI
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate
    logger.info("All required libraries imported successfully")
except ImportError as e:
    logger.error(f"Error importing required libraries: {e}")
    logger.info("Installing missing libraries...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", 
                          "pdfplumber", "unstructured", "camelot-py", "opencv-python", 
                          "openai", "langchain"])
    logger.info("Libraries installed, please run the script again")
    sys.exit(1)

class ComprehensiveExtractor:
    """Comprehensive extractor for financial documents."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the extractor."""
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "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")
        
        # Initialize OpenAI client
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Initialize LangChain
        self.llm = OpenAI(openai_api_key=self.api_key, temperature=0)
    
    def extract_with_pdfplumber(self, pdf_path: str) -> Dict[str, Any]:
        """Extract content using pdfplumber."""
        logger.info(f"Extracting content from {pdf_path} using pdfplumber")
        
        result = {"text": "", "tables": []}
        
        with pdfplumber.open(pdf_path) as pdf:
            logger.info(f"PDF has {len(pdf.pages)} pages")
            
            for i, page in enumerate(pdf.pages):
                logger.info(f"Processing page {i+1}/{len(pdf.pages)}")
                
                # Extract text
                text = page.extract_text() or ""
                result["text"] += f"\n\n--- Page {i+1} ---\n\n{text}"
                
                # Extract tables
                tables = page.extract_tables()
                for j, table in enumerate(tables):
                    result["tables"].append({
                        "page": i + 1,
                        "table_number": j + 1,
                        "data": table
                    })
        
        logger.info(f"Extracted {len(result['text'])} characters of text and {len(result['tables'])} tables")
        return result
    
    def extract_with_unstructured(self, pdf_path: str) -> Dict[str, Any]:
        """Extract content using unstructured."""
        logger.info(f"Extracting content from {pdf_path} using unstructured")
        
        result = {"elements": []}
        
        try:
            # Extract elements from PDF
            elements = partition_pdf(
                pdf_path,
                strategy="auto",
                languages=["eng"],
                ocr_enabled=True
            )
            
            # Process elements
            text_elements = []
            for element in elements:
                element_dict = {
                    "type": element.category,
                    "text": element.text,
                    "metadata": element.metadata.to_dict() if hasattr(element.metadata, "to_dict") else {}
                }
                result["elements"].append(element_dict)
                text_elements.append(element.text)
            
            # Combine text
            result["text"] = "\n\n".join(text_elements)
            
            logger.info(f"Extracted {len(result['elements'])} elements and {len(result['text'])} characters of text")
            return result
        
        except Exception as e:
            logger.error(f"Error extracting with unstructured: {e}")
            return {"elements": [], "text": ""}
    
    def extract_with_camelot(self, pdf_path: str) -> Dict[str, Any]:
        """Extract tables using camelot."""
        logger.info(f"Extracting tables from {pdf_path} using camelot")
        
        result = {"tables": []}
        
        try:
            # Try lattice mode first (for tables with borders)
            lattice_tables = camelot.read_pdf(pdf_path, pages="all", flavor="lattice")
            
            # Then try stream mode (for tables without borders)
            stream_tables = camelot.read_pdf(pdf_path, pages="all", flavor="stream")
            
            # Process lattice tables
            for i, table in enumerate(lattice_tables):
                result["tables"].append({
                    "page": table.page,
                    "extraction_method": "camelot_lattice",
                    "table_number": i + 1,
                    "data": table.data,
                    "headers": table.data[0] if len(table.data) > 0 else [],
                    "rows": table.data[1:] if len(table.data) > 1 else [],
                    "accuracy": table.accuracy
                })
            
            # Process stream tables
            for i, table in enumerate(stream_tables):
                result["tables"].append({
                    "page": table.page,
                    "extraction_method": "camelot_stream",
                    "table_number": i + 1,
                    "data": table.data,
                    "headers": table.data[0] if len(table.data) > 0 else [],
                    "rows": table.data[1:] if len(table.data) > 1 else [],
                    "accuracy": table.accuracy
                })
            
            logger.info(f"Extracted {len(result['tables'])} tables")
            return result
        
        except Exception as e:
            logger.error(f"Error extracting tables with camelot: {e}")
            return {"tables": []}
    
    def extract_securities(self, text: str) -> List[Dict[str, Any]]:
        """Extract securities from text using pattern matching and AI."""
        logger.info("Extracting securities from text")
        
        # Use AI to extract securities
        prompt = f"""
        Extract all securities (stocks, bonds, funds, etc.) from the following financial document text.
        For each security, provide:
        1. ISIN (if available)
        2. Name/Description
        3. Type (e.g., equity, bond, fund)
        4. Valuation (if available)
        5. Currency (if available)
        
        Format the output as a JSON array of objects.
        
        Text:
        {text[:10000]}  # Limit text to avoid token limits
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            
            # Extract JSON from response
            response_text = response.choices[0].message.content
            
            # Try to find JSON in the response
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
            else:
                # If no JSON code block, try to parse the whole response
                json_str = response_text
            
            # Find JSON array in the text
            json_array_match = re.search(r'\[\s*\{.*\}\s*\]', json_str, re.DOTALL)
            if json_array_match:
                json_str = json_array_match.group(0)
            
            # Parse JSON
            securities = json.loads(json_str)
            logger.info(f"Extracted {len(securities)} securities using AI")
            return securities
        
        except Exception as e:
            logger.error(f"Error extracting securities with AI: {e}")
            return []
    
    def extract_portfolio_value(self, text: str) -> Optional[float]:
        """Extract portfolio value from text."""
        logger.info("Extracting portfolio value from text")
        
        # Use AI to extract portfolio value
        prompt = f"""
        Extract the total portfolio value from the following financial document text.
        Return only the numeric value without currency symbols or formatting.
        
        Text:
        {text[:5000]}  # Limit text to avoid token limits
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            
            # Extract value from response
            response_text = response.choices[0].message.content
            
            # Try to find a number in the response
            import re
            value_match = re.search(r'(\d[\d,.\']*)', response_text)
            
            if value_match:
                value_str = value_match.group(1)
                value_str = value_str.replace("'", "").replace(",", "")
                try:
                    return float(value_str)
                except ValueError:
                    logger.error(f"Error converting portfolio value to float: {value_str}")
                    return None
            else:
                logger.error(f"No portfolio value found in response: {response_text}")
                return None
        
        except Exception as e:
            logger.error(f"Error extracting portfolio value with AI: {e}")
            return None
    
    def analyze_document(self, text: str) -> Dict[str, Any]:
        """Analyze the document using AI."""
        logger.info("Analyzing document with AI")
        
        # Use AI to analyze the document
        prompt = f"""
        Analyze the following financial document and provide:
        1. Document type
        2. Portfolio summary
        3. Asset allocation
        4. Top holdings
        5. Key insights
        
        Format the output as a JSON object.
        
        Text:
        {text[:15000]}  # Limit text to avoid token limits
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            
            # Extract JSON from response
            response_text = response.choices[0].message.content
            
            # Try to find JSON in the response
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
            else:
                # If no JSON code block, try to parse the whole response
                json_str = response_text
            
            # Find JSON object in the text
            json_object_match = re.search(r'\{\s*".*"\s*:.*\}', json_str, re.DOTALL)
            if json_object_match:
                json_str = json_object_match.group(0)
            
            # Parse JSON
            analysis = json.loads(json_str)
            logger.info("Document analysis completed")
            return analysis
        
        except Exception as e:
            logger.error(f"Error analyzing document with AI: {e}")
            return {
                "document_type": "Unknown",
                "portfolio_summary": "Error analyzing document",
                "asset_allocation": [],
                "top_holdings": [],
                "key_insights": []
            }
    
    def answer_question(self, text: str, question: str) -> str:
        """Answer a question about the document using AI."""
        logger.info(f"Answering question: {question}")
        
        # Use AI to answer the question
        prompt = f"""
        Based on the following financial document, answer this question:
        
        Question: {question}
        
        Document:
        {text[:15000]}  # Limit text to avoid token limits
        
        Provide a detailed and accurate answer based only on the information in the document.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            
            # Extract answer from response
            answer = response.choices[0].message.content
            logger.info(f"Question answered: {question}")
            return answer
        
        except Exception as e:
            logger.error(f"Error answering question with AI: {e}")
            return f"Error answering question: {e}"
    
    def process_document(self, pdf_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """Process a document comprehensively."""
        logger.info(f"Processing document: {pdf_path}")
        
        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Extract content using different methods
        pdfplumber_result = self.extract_with_pdfplumber(pdf_path)
        unstructured_result = self.extract_with_unstructured(pdf_path)
        camelot_result = self.extract_with_camelot(pdf_path)
        
        # Combine text from different extractors
        combined_text = pdfplumber_result.get("text", "") + "\n\n" + unstructured_result.get("text", "")
        
        # Extract securities
        securities = self.extract_securities(combined_text)
        
        # Extract portfolio value
        portfolio_value = self.extract_portfolio_value(combined_text)
        
        # Analyze document
        analysis = self.analyze_document(combined_text)
        
        # Answer some sample questions
        questions = [
            "What is the total portfolio value?",
            "What are the top 5 holdings?",
            "What is the asset allocation?",
            "What is the currency of the portfolio?",
            "What is the risk profile of the portfolio?"
        ]
        
        answers = {}
        for question in questions:
            answers[question] = self.answer_question(combined_text, question)
        
        # Combine results
        result = {
            "extraction": {
                "pdfplumber": {
                    "text_length": len(pdfplumber_result.get("text", "")),
                    "tables_count": len(pdfplumber_result.get("tables", []))
                },
                "unstructured": {
                    "text_length": len(unstructured_result.get("text", "")),
                    "elements_count": len(unstructured_result.get("elements", []))
                },
                "camelot": {
                    "tables_count": len(camelot_result.get("tables", []))
                }
            },
            "securities": securities,
            "portfolio_value": portfolio_value,
            "analysis": analysis,
            "answers": answers
        }
        
        # Save results if output directory is specified
        if output_dir:
            # Save combined text
            with open(os.path.join(output_dir, "combined_text.txt"), "w", encoding="utf-8") as f:
                f.write(combined_text)
            
            # Save pdfplumber text
            with open(os.path.join(output_dir, "pdfplumber_text.txt"), "w", encoding="utf-8") as f:
                f.write(pdfplumber_result.get("text", ""))
            
            # Save unstructured text
            with open(os.path.join(output_dir, "unstructured_text.txt"), "w", encoding="utf-8") as f:
                f.write(unstructured_result.get("text", ""))
            
            # Save securities
            with open(os.path.join(output_dir, "securities.json"), "w", encoding="utf-8") as f:
                json.dump(securities, f, indent=2)
            
            # Save analysis
            with open(os.path.join(output_dir, "analysis.json"), "w", encoding="utf-8") as f:
                json.dump(analysis, f, indent=2)
            
            # Save answers
            with open(os.path.join(output_dir, "answers.json"), "w", encoding="utf-8") as f:
                json.dump(answers, f, indent=2)
            
            # Save full result
            with open(os.path.join(output_dir, "result.json"), "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
        
        logger.info(f"Document processing completed: {pdf_path}")
        return result

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive financial document processing")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--output-dir", help="Directory to save extracted data")
    parser.add_argument("--api-key", help="OpenAI API key")
    
    args = parser.parse_args()
    
    # Process document
    extractor = ComprehensiveExtractor(api_key=args.api_key)
    result = extractor.process_document(args.pdf_path, args.output_dir)
    
    # Print summary
    print("\n" + "=" * 80)
    print("DOCUMENT PROCESSING SUMMARY")
    print("=" * 80)
    
    print(f"\nExtraction Statistics:")
    print(f"- PDFPlumber: {result['extraction']['pdfplumber']['text_length']} chars, {result['extraction']['pdfplumber']['tables_count']} tables")
    print(f"- Unstructured: {result['extraction']['unstructured']['text_length']} chars, {result['extraction']['unstructured']['elements_count']} elements")
    print(f"- Camelot: {result['extraction']['camelot']['tables_count']} tables")
    
    print(f"\nPortfolio Value: ${result['portfolio_value']:,.2f}" if result['portfolio_value'] else "\nPortfolio Value: Not found")
    
    print(f"\nSecurities: {len(result['securities'])}")
    for i, security in enumerate(result['securities'][:5]):  # Show top 5
        print(f"- {security.get('name', 'Unknown')}: {security.get('valuation', 'N/A')} {security.get('currency', '')}")
    if len(result['securities']) > 5:
        print(f"... and {len(result['securities']) - 5} more")
    
    print(f"\nDocument Type: {result['analysis'].get('document_type', 'Unknown')}")
    
    print(f"\nSample Q&A:")
    for question, answer in result['answers'].items():
        print(f"Q: {question}")
        print(f"A: {answer[:100]}..." if len(answer) > 100 else f"A: {answer}")
        print()
    
    print("\nResults saved to:", args.output_dir if args.output_dir else "Not saved")

if __name__ == "__main__":
    main()
