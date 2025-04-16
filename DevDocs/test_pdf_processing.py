"""
Test script to process a PDF file with all agents.
"""
import os
import sys
import argparse
import json
import cv2
import numpy as np
import pytesseract
from pathlib import Path
from datetime import datetime
import PyPDF2
from PIL import Image
import tempfile

# Add the parent directory to the path so we can import the backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF."""
    print(f"Extracting text from PDF: {pdf_path}")
    try:
        # Open the PDF file
        with open(pdf_path, 'rb') as file:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)

            # Get the number of pages
            num_pages = len(pdf_reader.pages)
            print(f"PDF has {num_pages} pages")

            # Extract text from each page
            all_text = ""
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                all_text += text + "\n\n"

            return all_text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def save_images(images, output_dir):
    """Save images to output directory."""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    image_paths = []
    for i, img in enumerate(images):
        image_path = output_dir / f"page_{i+1}.png"
        cv2.imwrite(str(image_path), img)
        image_paths.append(image_path)

    return image_paths

def test_document_preprocessor(images, output_dir):
    """Test DocumentPreprocessorAgent."""
    try:
        from DevDocs.backend.agents.document_preprocessor_agent import DocumentPreprocessorAgent

        print("\n=== Testing DocumentPreprocessorAgent ===\n")

        # Create the agent
        agent = DocumentPreprocessorAgent(output_dir=str(output_dir))

        results = []
        for i, image in enumerate(images):
            print(f"Processing page {i+1}...")

            # Process the image
            result = agent.process({"image": image})

            # Save the result
            results.append(result)

            print(f"Processed page {i+1}")
            if "preprocessed_image" in result:
                print(f"Preprocessed image shape: {result['preprocessed_image'].shape}")
            if "text_regions" in result:
                print(f"Detected {len(result['text_regions'])} text regions")

        return results
    except Exception as e:
        print(f"Error testing DocumentPreprocessorAgent: {e}")
        return []

def test_hebrew_ocr(images, output_dir):
    """Test HebrewOCRAgent."""
    try:
        from DevDocs.backend.agents.hebrew_ocr_agent import HebrewOCRAgent

        print("\n=== Testing HebrewOCRAgent ===\n")

        # Create the agent
        agent = HebrewOCRAgent()

        results = []
        for i, image in enumerate(images):
            print(f"Processing page {i+1}...")

            try:
                # Process the image
                result = agent.process({"image": image, "with_positions": True})

                # Save the result
                results.append(result)

                print(f"Processed page {i+1}")
                if "text" in result:
                    print(f"Extracted text length: {len(result['text'])}")

                    # Save the extracted text
                    text_path = output_dir / f"page_{i+1}_text.txt"
                    with open(text_path, "w", encoding="utf-8") as f:
                        f.write(result["text"])
                    print(f"Saved extracted text to {text_path}")
            except Exception as e:
                print(f"Error processing page {i+1}: {e}")
                results.append({"error": str(e)})

        return results
    except Exception as e:
        print(f"Error testing HebrewOCRAgent: {e}")
        return []

def test_isin_extractor(text, output_dir):
    """Test ISINExtractorAgent."""
    try:
        from DevDocs.backend.agents.isin_extractor_agent import ISINExtractorAgent

        print("\n=== Testing ISINExtractorAgent ===\n")

        # Create the agent
        agent = ISINExtractorAgent()

        # Process the text
        result = agent.process({"text": text, "validate": True, "with_metadata": True})

        print(f"Processed text")
        if "isins" in result:
            print(f"Extracted {len(result['isins'])} ISINs")

            # Save the extracted ISINs
            isins_path = output_dir / "extracted_isins.json"
            with open(isins_path, "w", encoding="utf-8") as f:
                json.dump(result["isins"], f, indent=2)
            print(f"Saved extracted ISINs to {isins_path}")

        return result
    except Exception as e:
        print(f"Error testing ISINExtractorAgent: {e}")
        return {"error": str(e)}

def test_financial_table_detector(images, output_dir, api_key=None):
    """Test FinancialTableDetectorAgent."""
    try:
        from DevDocs.backend.agents.financial_table_detector_agent import FinancialTableDetectorAgent

        print("\n=== Testing FinancialTableDetectorAgent ===\n")

        # Check for API key
        if not api_key:
            print("Warning: No API key provided. FinancialTableDetectorAgent may not work properly.")

        # Create the agent
        agent = FinancialTableDetectorAgent(api_key=api_key)

        results = []
        for i, image in enumerate(images):
            print(f"Processing page {i+1}...")

            try:
                # Process the image
                result = agent.process({"image": image, "language": "heb"})

                # Save the result
                results.append(result)

                print(f"Processed page {i+1}")
                if "tables" in result:
                    print(f"Detected {len(result['tables'])} tables")

                    # Save the detected tables
                    tables_path = output_dir / f"page_{i+1}_tables.json"
                    with open(tables_path, "w", encoding="utf-8") as f:
                        # Clean the tables for JSON serialization
                        clean_tables = []
                        for table in result["tables"]:
                            clean_table = {}
                            for k, v in table.items():
                                if isinstance(v, np.ndarray):
                                    clean_table[k] = v.tolist()
                                else:
                                    clean_table[k] = v
                            clean_tables.append(clean_table)

                        json.dump(clean_tables, f, indent=2)
                    print(f"Saved detected tables to {tables_path}")

                    # Save table images if available
                    if "table_images" in result:
                        for j, table_img in enumerate(result["table_images"]):
                            table_img_path = output_dir / f"page_{i+1}_table_{j+1}.png"
                            cv2.imwrite(str(table_img_path), table_img)
                            print(f"Saved table image to {table_img_path}")
            except Exception as e:
                print(f"Error processing page {i+1}: {e}")
                results.append({"error": str(e)})

        return results
    except Exception as e:
        print(f"Error testing FinancialTableDetectorAgent: {e}")
        return []

def test_document_merge(extracted_data, output_dir):
    """Test DocumentMergeAgent."""
    try:
        from DevDocs.backend.agents.document_merge_agent import DocumentMergeAgent

        print("\n=== Testing DocumentMergeAgent ===\n")

        # Create the agent
        agent = DocumentMergeAgent()

        # Create a sample document from extracted data
        documents = []

        # Add tables if available
        if "tables" in extracted_data:
            document = {
                "metadata": {
                    "document_type": "financial_statement",
                    "document_date": datetime.now().isoformat()
                },
                "tables": extracted_data["tables"],
                "financial_data": {
                    "tables": extracted_data["tables"]
                }
            }
            documents.append(document)

        # Add ISINs if available
        if "isins" in extracted_data:
            document = {
                "metadata": {
                    "document_type": "portfolio_statement",
                    "document_date": datetime.now().isoformat()
                },
                "financial_data": {
                    "securities": [
                        {"isin": isin} for isin in extracted_data["isins"]
                    ]
                }
            }
            documents.append(document)

        if not documents:
            print("No documents to merge")
            return {"error": "No documents to merge"}

        # Merge the documents
        result = agent.merge_documents(documents)

        print(f"Merged {len(documents)} documents")

        # Save the merged document
        merged_path = output_dir / "merged_document.json"
        with open(merged_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"Saved merged document to {merged_path}")

        return result
    except Exception as e:
        print(f"Error testing DocumentMergeAgent: {e}")
        return {"error": str(e)}

def main():
    """Process a PDF file with all agents."""
    parser = argparse.ArgumentParser(description="Process a PDF file with all agents")
    parser.add_argument("--pdf", default="messos.pdf", help="Path to the PDF file")
    parser.add_argument("--api-key", help="OpenRouter API key")
    parser.add_argument("--output-dir", default="./pdf_processing_results", help="Output directory")
    args = parser.parse_args()

    # Get API key from arguments or environment
    api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Warning: No API key provided. Some agents may not work properly.")

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    # Check if PDF file exists
    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        return 1

    print(f"Processing PDF file: {pdf_path}")

    # Extract text from PDF
    all_text = extract_text_from_pdf(pdf_path)
    if not all_text:
        print("Error: Failed to extract text from PDF")
        return 1

    # Save all extracted text
    all_text_path = output_dir / "all_text.txt"
    with open(all_text_path, "w", encoding="utf-8") as f:
        f.write(all_text)
    print(f"Saved all extracted text to {all_text_path}")

    # Process with ISINExtractorAgent
    isin_results = test_isin_extractor(all_text, output_dir / "isins")

    # Combine all extracted data
    extracted_data = {
        "text": all_text,
        "isins": isin_results.get("isins", []),
        "tables": []
    }

    # Save all extracted data
    extracted_data_path = output_dir / "extracted_data.json"
    with open(extracted_data_path, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, indent=2)
    print(f"Saved all extracted data to {extracted_data_path}")

    # Process with DocumentMergeAgent
    merge_result = test_document_merge(extracted_data, output_dir / "merged")

    print("\nAll processing completed!")
    print(f"Results saved to {output_dir}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
