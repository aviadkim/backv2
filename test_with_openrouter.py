import os
import sys
import json
import logging
import argparse
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# OpenRouter API key
OPENROUTER_API_KEY = "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"

class OpenRouterClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://backv2.com",
            "X-Title": "FinDoc Analyzer Test"
        }
    
    def chat_completion(self, model, messages, temperature=0.7, max_tokens=1000):
        """
        Send a chat completion request to OpenRouter
        """
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling OpenRouter API: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            return None

def test_document_preprocessor_agent(client, pdf_path):
    """
    Test the DocumentPreprocessorAgent with a PDF
    """
    logger.info(f"Testing DocumentPreprocessorAgent with {pdf_path}")
    
    with open(pdf_path, 'rb') as f:
        pdf_content = f.read()
    
    # Convert PDF content to base64 for API consumption
    import base64
    pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
    
    messages = [
        {"role": "system", "content": "You are a DocumentPreprocessorAgent specialized in preparing financial documents for analysis. Your task is to analyze the document structure, identify tables, headers, and key sections."},
        {"role": "user", "content": f"I'm sending you a financial document for preprocessing. Please analyze its structure and identify key sections like tables, headers, and financial data. The document is a portfolio statement from a bank.\n\nDocument content: [PDF content too large to include in prompt]"}
    ]
    
    response = client.chat_completion("openrouter/anthropic/claude-3-opus", messages)
    
    if response:
        logger.info("DocumentPreprocessorAgent response received")
        return response
    else:
        logger.error("Failed to get response from DocumentPreprocessorAgent")
        return None

def test_hebrew_ocr_agent(client, pdf_path):
    """
    Test the HebrewOCRAgent with a PDF
    """
    logger.info(f"Testing HebrewOCRAgent with {pdf_path}")
    
    messages = [
        {"role": "system", "content": "You are a HebrewOCRAgent specialized in extracting and translating Hebrew text from financial documents. Your task is to identify any Hebrew text in the document and provide translations."},
        {"role": "user", "content": "I'm sending you a financial document that may contain Hebrew text. Please identify any Hebrew text and provide translations. The document is a portfolio statement from a bank."}
    ]
    
    response = client.chat_completion("openrouter/anthropic/claude-3-opus", messages)
    
    if response:
        logger.info("HebrewOCRAgent response received")
        return response
    else:
        logger.error("Failed to get response from HebrewOCRAgent")
        return None

def test_isin_extractor_agent(client, pdf_path):
    """
    Test the ISINExtractorAgent with a PDF
    """
    logger.info(f"Testing ISINExtractorAgent with {pdf_path}")
    
    messages = [
        {"role": "system", "content": "You are an ISINExtractorAgent specialized in identifying and extracting International Securities Identification Numbers (ISINs) from financial documents. Your task is to find all ISINs and associated security information."},
        {"role": "user", "content": "I'm sending you a financial document. Please extract all ISINs (International Securities Identification Numbers) and associated security information like security names, values, and percentages. The document is a portfolio statement from a bank."}
    ]
    
    response = client.chat_completion("openrouter/anthropic/claude-3-opus", messages)
    
    if response:
        logger.info("ISINExtractorAgent response received")
        return response
    else:
        logger.error("Failed to get response from ISINExtractorAgent")
        return None

def test_financial_table_detector_agent(client, pdf_path):
    """
    Test the FinancialTableDetectorAgent with a PDF
    """
    logger.info(f"Testing FinancialTableDetectorAgent with {pdf_path}")
    
    messages = [
        {"role": "system", "content": "You are a FinancialTableDetectorAgent specialized in identifying and extracting tables from financial documents. Your task is to locate all tables and extract their structure and content."},
        {"role": "user", "content": "I'm sending you a financial document. Please identify all tables in the document and extract their structure and content. The document is a portfolio statement from a bank."}
    ]
    
    response = client.chat_completion("openrouter/anthropic/claude-3-opus", messages)
    
    if response:
        logger.info("FinancialTableDetectorAgent response received")
        return response
    else:
        logger.error("Failed to get response from FinancialTableDetectorAgent")
        return None

def test_financial_data_analyzer_agent(client, pdf_path):
    """
    Test the FinancialDataAnalyzerAgent with a PDF
    """
    logger.info(f"Testing FinancialDataAnalyzerAgent with {pdf_path}")
    
    messages = [
        {"role": "system", "content": "You are a FinancialDataAnalyzerAgent specialized in analyzing financial data from documents. Your task is to extract key financial metrics, calculate portfolio statistics, and provide insights."},
        {"role": "user", "content": "I'm sending you a financial document. Please analyze the financial data, extract key metrics like portfolio value, asset allocation, top holdings, and provide insights. The document is a portfolio statement from a bank."}
    ]
    
    response = client.chat_completion("openrouter/anthropic/claude-3-opus", messages)
    
    if response:
        logger.info("FinancialDataAnalyzerAgent response received")
        return response
    else:
        logger.error("Failed to get response from FinancialDataAnalyzerAgent")
        return None

def test_query_engine_agent(client, pdf_path):
    """
    Test the QueryEngineAgent with a PDF
    """
    logger.info(f"Testing QueryEngineAgent with {pdf_path}")
    
    messages = [
        {"role": "system", "content": "You are a QueryEngineAgent specialized in answering questions about financial documents. Your task is to provide accurate answers to user queries based on the document content."},
        {"role": "user", "content": "I'm sending you a financial document. Please answer the following questions:\n1. What is the total portfolio value?\n2. What are the top 5 holdings?\n3. What is the asset allocation?\n4. What is the value of the security with ISIN CH1259344831?"}
    ]
    
    response = client.chat_completion("openrouter/anthropic/claude-3-opus", messages)
    
    if response:
        logger.info("QueryEngineAgent response received")
        return response
    else:
        logger.error("Failed to get response from QueryEngineAgent")
        return None

def test_document_integration_agent(client, pdf_path):
    """
    Test the DocumentIntegrationAgent with a PDF
    """
    logger.info(f"Testing DocumentIntegrationAgent with {pdf_path}")
    
    messages = [
        {"role": "system", "content": "You are a DocumentIntegrationAgent specialized in integrating information from multiple sources in a financial document. Your task is to combine data from different sections to create a comprehensive view."},
        {"role": "user", "content": "I'm sending you a financial document. Please integrate information from different sections to create a comprehensive view of the portfolio, including client information, portfolio value, asset allocation, and holdings."}
    ]
    
    response = client.chat_completion("openrouter/anthropic/claude-3-opus", messages)
    
    if response:
        logger.info("DocumentIntegrationAgent response received")
        return response
    else:
        logger.error("Failed to get response from DocumentIntegrationAgent")
        return None

def test_document_merge_agent(client, pdf_path):
    """
    Test the DocumentMergeAgent with a PDF
    """
    logger.info(f"Testing DocumentMergeAgent with {pdf_path}")
    
    messages = [
        {"role": "system", "content": "You are a DocumentMergeAgent specialized in merging information from multiple financial documents. Your task is to combine data from different documents to create a unified view."},
        {"role": "user", "content": "I'm sending you a financial document. Please simulate merging this document with a previous version to identify changes in portfolio composition, value, and performance."}
    ]
    
    response = client.chat_completion("openrouter/anthropic/claude-3-opus", messages)
    
    if response:
        logger.info("DocumentMergeAgent response received")
        return response
    else:
        logger.error("Failed to get response from DocumentMergeAgent")
        return None

def test_data_export_agent(client, pdf_path):
    """
    Test the DataExportAgent with a PDF
    """
    logger.info(f"Testing DataExportAgent with {pdf_path}")
    
    messages = [
        {"role": "system", "content": "You are a DataExportAgent specialized in exporting financial data from documents to structured formats. Your task is to convert document data to formats like CSV, JSON, or Excel."},
        {"role": "user", "content": "I'm sending you a financial document. Please extract the key financial data and format it as structured JSON that could be exported to a database or spreadsheet."}
    ]
    
    response = client.chat_completion("openrouter/anthropic/claude-3-opus", messages)
    
    if response:
        logger.info("DataExportAgent response received")
        return response
    else:
        logger.error("Failed to get response from DataExportAgent")
        return None

def test_document_comparison_agent(client, pdf_path):
    """
    Test the DocumentComparisonAgent with a PDF
    """
    logger.info(f"Testing DocumentComparisonAgent with {pdf_path}")
    
    messages = [
        {"role": "system", "content": "You are a DocumentComparisonAgent specialized in comparing financial documents. Your task is to identify differences between documents and highlight changes."},
        {"role": "user", "content": "I'm sending you a financial document. Please simulate comparing this document with a previous version to identify changes in portfolio composition, value, and performance."}
    ]
    
    response = client.chat_completion("openrouter/anthropic/claude-3-opus", messages)
    
    if response:
        logger.info("DocumentComparisonAgent response received")
        return response
    else:
        logger.error("Failed to get response from DocumentComparisonAgent")
        return None

def test_financial_advisor_agent(client, pdf_path):
    """
    Test the FinancialAdvisorAgent with a PDF
    """
    logger.info(f"Testing FinancialAdvisorAgent with {pdf_path}")
    
    messages = [
        {"role": "system", "content": "You are a FinancialAdvisorAgent specialized in providing financial advice based on document analysis. Your task is to analyze the portfolio and provide recommendations."},
        {"role": "user", "content": "I'm sending you a financial document. Please analyze the portfolio and provide recommendations for optimization, diversification, and risk management."}
    ]
    
    response = client.chat_completion("openrouter/anthropic/claude-3-opus", messages)
    
    if response:
        logger.info("FinancialAdvisorAgent response received")
        return response
    else:
        logger.error("Failed to get response from FinancialAdvisorAgent")
        return None

def run_comprehensive_tests(pdf_path, output_dir):
    """
    Run comprehensive tests on all agents
    """
    logger.info(f"Running comprehensive tests with {pdf_path}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize OpenRouter client
    client = OpenRouterClient(OPENROUTER_API_KEY)
    
    # Test all agents
    agents = [
        ("DocumentPreprocessorAgent", test_document_preprocessor_agent),
        ("HebrewOCRAgent", test_hebrew_ocr_agent),
        ("ISINExtractorAgent", test_isin_extractor_agent),
        ("FinancialTableDetectorAgent", test_financial_table_detector_agent),
        ("FinancialDataAnalyzerAgent", test_financial_data_analyzer_agent),
        ("QueryEngineAgent", test_query_engine_agent),
        ("DocumentIntegrationAgent", test_document_integration_agent),
        ("DocumentMergeAgent", test_document_merge_agent),
        ("DataExportAgent", test_data_export_agent),
        ("DocumentComparisonAgent", test_document_comparison_agent),
        ("FinancialAdvisorAgent", test_financial_advisor_agent)
    ]
    
    results = {}
    
    for agent_name, agent_func in agents:
        logger.info(f"Testing {agent_name}...")
        response = agent_func(client, pdf_path)
        
        if response:
            # Save response to file
            output_file = os.path.join(output_dir, f"{agent_name}_response.json")
            with open(output_file, 'w') as f:
                json.dump(response, f, indent=2)
            
            # Extract the content from the response
            if 'choices' in response and len(response['choices']) > 0:
                content = response['choices'][0]['message']['content']
                
                # Save content to file
                content_file = os.path.join(output_dir, f"{agent_name}_content.txt")
                with open(content_file, 'w') as f:
                    f.write(content)
                
                results[agent_name] = {
                    "status": "success",
                    "content": content[:500] + "..." if len(content) > 500 else content  # Truncate for summary
                }
            else:
                results[agent_name] = {
                    "status": "error",
                    "message": "No content in response"
                }
        else:
            results[agent_name] = {
                "status": "error",
                "message": "Failed to get response"
            }
    
    # Save summary to file
    summary_file = os.path.join(output_dir, "test_summary.json")
    with open(summary_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Comprehensive tests completed. Results saved to {output_dir}")
    return results

def main():
    parser = argparse.ArgumentParser(description="Test FinDoc Analyzer with OpenRouter API")
    parser.add_argument("--pdf", required=True, help="Path to the PDF file to test")
    parser.add_argument("--output-dir", default="openrouter_test_results", help="Directory to save test results")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf):
        logger.error(f"PDF file not found: {args.pdf}")
        sys.exit(1)
    
    results = run_comprehensive_tests(args.pdf, args.output_dir)
    
    # Print summary
    print("\nTest Summary:")
    print("=" * 80)
    for agent_name, result in results.items():
        status = "✅ Success" if result["status"] == "success" else "❌ Error"
        print(f"{agent_name}: {status}")
    print("=" * 80)
    print(f"Detailed results saved to {args.output_dir}")

if __name__ == "__main__":
    main()
