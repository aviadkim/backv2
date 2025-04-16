"""
Script to merge all the extracted data from the Messos PDF.
"""
import os
import sys
import json
from pathlib import Path

# Add the parent directory to the path so we can import the backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def merge_messos_data():
    """Merge all the extracted data from the Messos PDF."""
    try:
        from DevDocs.backend.agents.document_merge_agent import DocumentMergeAgent
        
        print("\n=== Merging Messos PDF Data ===\n")
        
        # Create output directory
        output_dir = Path("./messos_results")
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Load the extracted ISINs
        isins_path = output_dir / "extracted_isins.json"
        if not isins_path.exists():
            print(f"Error: ISINs file not found: {isins_path}")
            return None
        
        with open(isins_path, 'r', encoding='utf-8') as f:
            isins_data = json.load(f)
        
        # Load the extracted tables
        tables_path = output_dir / "extracted_tables.json"
        if not tables_path.exists():
            print(f"Error: Tables file not found: {tables_path}")
            return None
        
        with open(tables_path, 'r', encoding='utf-8') as f:
            tables_data = json.load(f)
        
        # Create a document from the extracted data
        document = {
            "metadata": {
                "document_type": "portfolio_statement",
                "document_date": "2025-02-28",
                "client_name": "MESSOS ENTERPRISES LTD.",
                "client_number": "366223",
                "valuation_currency": "USD"
            },
            "tables": [],
            "financial_data": {
                "portfolio": {
                    "securities": [],
                    "summary": {
                        "total_value": 19510599,
                        "total_securities": 0
                    }
                },
                "isins": []
            }
        }
        
        # Add tables
        for table_name, table_data in tables_data.items():
            if table_data:
                document["tables"].append({
                    "type": table_name,
                    "data": table_data
                })
        
        # Add securities from bonds table
        securities_count = 0
        if tables_data["bonds"]:
            for bond in tables_data["bonds"]:
                try:
                    security = {
                        "type": "bond",
                        "isin": bond["ISIN"],
                        "description": bond["Description"],
                        "currency": bond["Currency"],
                        "nominal": bond["Nominal"],
                        "price": 0,
                        "value": 0,
                        "weight": 0
                    }
                    
                    # Try to convert price, value, and weight to numbers
                    if bond["Price"] != "N/A":
                        try:
                            security["price"] = float(bond["Price"])
                        except:
                            pass
                    
                    if bond["Value (USD)"] != "N/A":
                        try:
                            security["value"] = float(bond["Value (USD)"])
                        except:
                            pass
                    
                    if bond["Weight (%)"] != "N/A":
                        try:
                            security["weight"] = float(bond["Weight (%)"])
                        except:
                            pass
                    
                    document["financial_data"]["portfolio"]["securities"].append(security)
                    securities_count += 1
                except Exception as e:
                    print(f"Error adding bond: {e}")
        
        # Add securities from structured products table
        if tables_data["structured_products"]:
            for product in tables_data["structured_products"]:
                try:
                    security = {
                        "type": "structured_product",
                        "isin": product["ISIN"],
                        "description": product["Description"],
                        "currency": product["Currency"],
                        "nominal": product["Nominal"],
                        "price": 0,
                        "value": 0,
                        "weight": 0
                    }
                    
                    # Try to convert price, value, and weight to numbers
                    if product["Price"] != "N/A":
                        try:
                            security["price"] = float(product["Price"])
                        except:
                            pass
                    
                    if product["Value (USD)"] != "N/A":
                        try:
                            security["value"] = float(product["Value (USD)"])
                        except:
                            pass
                    
                    if product["Weight (%)"] != "N/A":
                        try:
                            security["weight"] = float(product["Weight (%)"])
                        except:
                            pass
                    
                    document["financial_data"]["portfolio"]["securities"].append(security)
                    securities_count += 1
                except Exception as e:
                    print(f"Error adding structured product: {e}")
        
        # Update total securities count
        document["financial_data"]["portfolio"]["summary"]["total_securities"] = securities_count
        
        # Add ISINs
        for isin_data in isins_data:
            if isinstance(isin_data, dict) and "isin" in isin_data:
                document["financial_data"]["isins"].append(isin_data["isin"])
            else:
                document["financial_data"]["isins"].append(isin_data)
        
        # Create the agent
        agent = DocumentMergeAgent()
        
        # Merge the document
        merged_document = agent.merge_documents([document])
        
        # Save the merged document
        merged_path = output_dir / "merged_document.json"
        with open(merged_path, "w", encoding="utf-8") as f:
            json.dump(merged_document, f, indent=2)
        print(f"Saved merged document to {merged_path}")
        
        # Generate a comprehensive report
        try:
            report = agent.generate_comprehensive_report(merged_document)
            
            # Save the report
            report_path = output_dir / "comprehensive_report.json"
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            print(f"Saved comprehensive report to {report_path}")
        except Exception as e:
            print(f"Error generating comprehensive report: {e}")
        
        return merged_document
    except Exception as e:
        print(f"Error merging data: {e}")
        return None

if __name__ == "__main__":
    merge_messos_data()
