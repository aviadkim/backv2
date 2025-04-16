"""
Comprehensive Financial Document Processor

This script orchestrates multiple specialized agents to extract and understand
financial documents with human-like comprehension.
"""
import os
import sys
import argparse
import json
import time
from pathlib import Path

# Add the DevDocs directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "DevDocs"))

# Import agents
from DevDocs.backend.agents.agent_manager import AgentManager
from DevDocs.backend.agents.document_preprocessor_agent import DocumentPreprocessorAgent
from DevDocs.backend.agents.hebrew_ocr_agent import HebrewOCRAgent
from DevDocs.backend.agents.isin_extractor_agent import ISINExtractorAgent
from DevDocs.backend.agents.financial_table_detector_agent import FinancialTableDetectorAgent
from DevDocs.backend.agents.financial_data_analyzer_agent import FinancialDataAnalyzerAgent
from DevDocs.backend.agents.document_integration_agent import DocumentIntegrationAgent
from DevDocs.backend.agents.query_engine_agent import QueryEngineAgent
from DevDocs.backend.agents.document_merge_agent import DocumentMergeAgent

def process_document(pdf_path, api_key, output_dir="comprehensive_results"):
    """
    Process a financial document with all available agents.
    
    Args:
        pdf_path: Path to the PDF file
        api_key: OpenRouter API key
        output_dir: Output directory
    
    Returns:
        Dictionary with processing results
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Processing document: {pdf_path}")
    
    # Create agent manager
    manager = AgentManager(api_key=api_key)
    
    # Step 1: Document Preprocessing
    print("\n=== Step 1: Document Preprocessing ===")
    manager.create_agent(
        "preprocessor",
        DocumentPreprocessorAgent,
        output_dir=os.path.join(output_dir, "preprocessed")
    )
    preprocessed_result = manager.run_agent("preprocessor", pdf_path=pdf_path)
    
    # Save preprocessed result
    with open(os.path.join(output_dir, "preprocessed_result.json"), "w", encoding="utf-8") as f:
        json.dump(preprocessed_result, f, indent=2)
    
    # Step 2: OCR Processing
    print("\n=== Step 2: OCR Processing ===")
    manager.create_agent(
        "ocr",
        HebrewOCRAgent
    )
    ocr_result = manager.run_agent("ocr", image_path=preprocessed_result.get("output_path", pdf_path), lang="heb+eng")
    
    # Save OCR result
    with open(os.path.join(output_dir, "ocr_result.json"), "w", encoding="utf-8") as f:
        json.dump(ocr_result, f, indent=2)
    
    # Save extracted text
    with open(os.path.join(output_dir, "extracted_text.txt"), "w", encoding="utf-8") as f:
        f.write(ocr_result.get("text", ""))
    
    # Step 3: Table Detection
    print("\n=== Step 3: Table Detection ===")
    manager.create_agent(
        "table_detector",
        FinancialTableDetectorAgent,
        api_key=api_key
    )
    table_result = manager.run_agent("table_detector", image_path=preprocessed_result.get("output_path", pdf_path))
    
    # Save table result
    with open(os.path.join(output_dir, "table_result.json"), "w", encoding="utf-8") as f:
        json.dump(table_result, f, indent=2)
    
    # Step 4: ISIN Extraction
    print("\n=== Step 4: ISIN Extraction ===")
    manager.create_agent(
        "isin_extractor",
        ISINExtractorAgent
    )
    isin_result = manager.run_agent("isin_extractor", text=ocr_result.get("text", ""), validate=True, with_metadata=True)
    
    # Save ISIN result
    with open(os.path.join(output_dir, "isin_result.json"), "w", encoding="utf-8") as f:
        json.dump(isin_result, f, indent=2)
    
    # Step 5: Financial Data Analysis
    print("\n=== Step 5: Financial Data Analysis ===")
    manager.create_agent(
        "data_analyzer",
        FinancialDataAnalyzerAgent,
        api_key=api_key
    )
    data_result = manager.run_agent("data_analyzer", text=ocr_result.get("text", ""), tables=table_result.get("tables", []))
    
    # Save data result
    with open(os.path.join(output_dir, "data_result.json"), "w", encoding="utf-8") as f:
        json.dump(data_result, f, indent=2)
    
    # Step 6: Document Integration
    print("\n=== Step 6: Document Integration ===")
    manager.create_agent(
        "document_integration",
        DocumentIntegrationAgent,
        api_key=api_key
    )
    integration_result = manager.run_agent(
        "document_integration", 
        text=ocr_result.get("text", ""), 
        tables=table_result.get("tables", []),
        isins=isin_result.get("isins", []),
        financial_data=data_result
    )
    
    # Save integration result
    with open(os.path.join(output_dir, "integration_result.json"), "w", encoding="utf-8") as f:
        json.dump(integration_result, f, indent=2)
    
    # Step 7: Document Merge
    print("\n=== Step 7: Document Merge ===")
    manager.create_agent(
        "document_merge",
        DocumentMergeAgent
    )
    merge_result = manager.run_agent(
        "document_merge",
        documents=[
            {"type": "text", "content": ocr_result.get("text", "")},
            {"type": "tables", "content": table_result.get("tables", [])},
            {"type": "isins", "content": isin_result.get("isins", [])},
            {"type": "financial_data", "content": data_result}
        ]
    )
    
    # Save merge result
    with open(os.path.join(output_dir, "merge_result.json"), "w", encoding="utf-8") as f:
        json.dump(merge_result, f, indent=2)
    
    # Step 8: Query Engine
    print("\n=== Step 8: Query Engine ===")
    manager.create_agent(
        "query_engine",
        QueryEngineAgent,
        api_key=api_key
    )
    
    # Ask specific questions about the document
    questions = [
        "What is the total portfolio value?",
        "How many securities are in the portfolio?",
        "What are the top 5 holdings by value?",
        "What is the asset allocation of the portfolio?",
        "What is the value of security with ISIN CH1259344831?",
        "What is the total value of structured products?",
        "Who is the client?",
        "What is the document date?"
    ]
    
    query_results = {}
    for question in questions:
        print(f"Question: {question}")
        query_result = manager.run_agent(
            "query_engine",
            question=question,
            document=merge_result.get("merged_document", {})
        )
        query_results[question] = query_result
        print(f"Answer: {query_result.get('answer', '')}\n")
    
    # Save query results
    with open(os.path.join(output_dir, "query_results.json"), "w", encoding="utf-8") as f:
        json.dump(query_results, f, indent=2)
    
    # Generate comprehensive report
    comprehensive_report = {
        "document_path": pdf_path,
        "processing_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "client_info": data_result.get("client_info", {}),
        "document_date": data_result.get("document_date", ""),
        "portfolio_value": data_result.get("portfolio_value", 0),
        "securities_count": len(isin_result.get("isins", [])),
        "asset_allocation": data_result.get("asset_allocation", {}),
        "top_holdings": data_result.get("top_holdings", []),
        "query_results": query_results
    }
    
    # Save comprehensive report
    with open(os.path.join(output_dir, "comprehensive_report.json"), "w", encoding="utf-8") as f:
        json.dump(comprehensive_report, f, indent=2)
    
    print(f"\nProcessing completed. Results saved to {output_dir}")
    
    return comprehensive_report

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Comprehensive Financial Document Processor")
    parser.add_argument("--pdf", required=True, help="Path to the PDF file")
    parser.add_argument("--api-key", required=True, help="OpenRouter API key")
    parser.add_argument("--output-dir", default="comprehensive_results", help="Output directory")
    args = parser.parse_args()
    
    process_document(args.pdf, args.api_key, args.output_dir)

if __name__ == "__main__":
    main()
