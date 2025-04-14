"""
Data Export Agent for exporting data to various formats.
"""
import json
import csv
import os
import pandas as pd
import xml.dom.minidom
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
from .base_agent import BaseAgent

class DataExportAgent(BaseAgent):
    """Agent for exporting data to various formats for use in other systems."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        output_dir: str = "exports",
        **kwargs
    ):
        """
        Initialize the data export agent.
        
        Args:
            api_key: OpenRouter API key
            output_dir: Directory for exported files
            **kwargs: Additional parameters for the base agent
        """
        super().__init__(name="Data Export Agent")
        self.api_key = api_key
        self.description = "I export data to various formats for use in other systems."
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task to export data.
        
        Args:
            task: Task dictionary with the following keys:
                - data: Data to export
                - format_type: Export format (json, csv, excel, xml)
                - filename: Optional filename
                - export_type: Optional export type (raw, portfolio_summary, isin_list)
                
        Returns:
            Dictionary with export results
        """
        # Get the required data
        data = task.get('data', {})
        format_type = task.get('format_type', 'json')
        filename = task.get('filename')
        export_type = task.get('export_type', 'raw')
        
        # Check if we have data to export
        if not data:
            return {
                'status': 'error',
                'message': 'No data provided for export'
            }
        
        # Perform the export based on type
        try:
            if export_type == 'portfolio_summary':
                filepath = self.export_portfolio_summary(data, format_type, filename)
            elif export_type == 'isin_list':
                filepath = self.export_isin_list(data, format_type, filename)
            else:
                # Raw data export
                filepath = self.export_data(data, format_type, filename)
            
            return {
                'status': 'success',
                'message': f'Data exported successfully to {filepath}',
                'filepath': filepath,
                'format': format_type,
                'export_type': export_type
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error exporting data: {str(e)}'
            }
    
    def export_data(self, data: Dict[str, Any], format_type: str, filename: Optional[str] = None) -> str:
        """
        Export data to the requested format.
        
        Args:
            data: Data to export
            format_type: Export format (json, csv, excel, xml)
            filename: Optional filename
            
        Returns:
            Path to the created file
        """
        # Create filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{timestamp}"
        
        # Export based on the requested format
        if format_type.lower() == "json":
            return self._export_to_json(data, filename)
        elif format_type.lower() == "csv":
            return self._export_to_csv(data, filename)
        elif format_type.lower() == "excel":
            return self._export_to_excel(data, filename)
        elif format_type.lower() == "xml":
            return self._export_to_xml(data, filename)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def _export_to_json(self, data: Dict[str, Any], filename: str) -> str:
        """Export to JSON format."""
        # Ensure filename has the correct extension
        if not filename.lower().endswith('.json'):
            filename += '.json'
            
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def _export_to_csv(self, data: Dict[str, Any], filename: str) -> str:
        """Export to CSV format."""
        # Ensure filename has the correct extension
        if not filename.lower().endswith('.csv'):
            filename += '.csv'
            
        filepath = os.path.join(self.output_dir, filename)
        
        # Convert data to tabular format
        tabular_data = self._convert_to_tabular(data)
        
        if not tabular_data:
            raise ValueError("Could not convert data to tabular format")
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write headers
            writer.writerow(tabular_data[0].keys())
            
            # Write rows
            for row in tabular_data:
                writer.writerow(row.values())
        
        return filepath
    
    def _export_to_excel(self, data: Dict[str, Any], filename: str) -> str:
        """Export to Excel format."""
        # Ensure filename has the correct extension
        if not filename.lower().endswith(('.xlsx', '.xls')):
            filename += '.xlsx'
            
        filepath = os.path.join(self.output_dir, filename)
        
        # Create Excel file with different sheets based on data type
        with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#CCCCCC',
                'border': 1
            })
            
            # Summary sheet
            summary_sheet = pd.DataFrame()
            summary_data = []
            
            # Add metadata
            if "metadata" in data:
                for key, value in data["metadata"].items():
                    summary_data.append({"Category": "Metadata", "Key": key, "Value": str(value)})
            
            # Add summary
            if "summary" in data:
                for key, value in data["summary"].items():
                    summary_data.append({"Category": "Summary", "Key": key, "Value": str(value)})
            
            if summary_data:
                summary_sheet = pd.DataFrame(summary_data)
                summary_sheet.to_excel(writer, sheet_name="Summary", index=False)
            
            # Tables sheets
            if "tables" in data:
                for i, table in enumerate(data["tables"]):
                    sheet_name = f"Table_{i+1}"
                    if "type" in table and table["type"] != "unknown":
                        sheet_name = table["type"]
                    
                    if "data" in table and table["data"]:
                        # Convert to DataFrame
                        if isinstance(table["data"], list):
                            df = pd.DataFrame(table["data"])
                            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Entities sheet
            if "entities" in data:
                entities_data = []
                
                for entity_type, entities in data["entities"].items():
                    if entities:
                        # Check if entities have a uniform structure
                        if isinstance(entities[0], dict):
                            for entity in entities:
                                entity_row = {"Entity Type": entity_type}
                                entity_row.update(entity)
                                entities_data.append(entity_row)
                        else:
                            # Simple list
                            for entity in entities:
                                entities_data.append({
                                    "Entity Type": entity_type,
                                    "Value": str(entity)
                                })
                
                if entities_data:
                    entities_df = pd.DataFrame(entities_data)
                    entities_df.to_excel(writer, sheet_name="Entities", index=False)
            
            # Financial data sheet
            if "financial_data" in data:
                for key, value in data["financial_data"].items():
                    if isinstance(value, dict) and "securities" in value:
                        securities_df = pd.DataFrame(value["securities"])
                        securities_df.to_excel(writer, sheet_name=f"{key.capitalize()}", index=False)
        
        return filepath
    
    def _export_to_xml(self, data: Dict[str, Any], filename: str) -> str:
        """Export to XML format."""
        # Ensure filename has the correct extension
        if not filename.lower().endswith('.xml'):
            filename += '.xml'
            
        filepath = os.path.join(self.output_dir, filename)
        
        # Create XML document
        doc = xml.dom.minidom.getDOMImplementation().createDocument(None, "document", None)
        root = doc.documentElement
        
        # Convert data to XML
        self._dict_to_xml(data, root, doc)
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(doc.toprettyxml(indent="  "))
        
        return filepath
    
    def _dict_to_xml(self, data, parent_node, doc):
        """Convert dictionary to XML recursively."""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    # Create a new element
                    child = doc.createElement(str(key))
                    parent_node.appendChild(child)
                    self._dict_to_xml(value, child, doc)
                else:
                    # Add element with content
                    child = doc.createElement(str(key))
                    parent_node.appendChild(child)
                    text = doc.createTextNode(str(value))
                    child.appendChild(text)
        elif isinstance(data, list):
            for item in data:
                # Create an "item" element
                child = doc.createElement("item")
                parent_node.appendChild(child)
                self._dict_to_xml(item, child, doc)
        else:
            # Add content directly
            text = doc.createTextNode(str(data))
            parent_node.appendChild(text)
    
    def _convert_to_tabular(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert data to tabular format (list of dictionaries)."""
        tabular_data = []
        
        # Try to find tabular data
        if "tables" in data:
            for table in data["tables"]:
                if "data" in table and table["data"]:
                    # If already in tabular format - return it
                    return table["data"]
        
        # Try to find financial data
        if "financial_data" in data:
            financial_data = data["financial_data"]
            
            # Check portfolio data
            if "portfolio" in financial_data and "securities" in financial_data["portfolio"]:
                return financial_data["portfolio"]["securities"]
        
        # Try to find entities
        if "entities" in data and "isin" in data["entities"]:
            return data["entities"]["isin"]
        
        # If no tabular data found
        return tabular_data
    
    def export_portfolio_summary(self, document_data: Dict[str, Any], format_type: str, filename: Optional[str] = None) -> str:
        """
        Export portfolio summary in a dedicated format.
        
        Args:
            document_data: Processed document data
            format_type: Export format
            filename: Optional filename
            
        Returns:
            Path to the created file
        """
        # Create portfolio summary data
        portfolio_summary = {
            "extraction_date": datetime.now().isoformat(),
            "document_id": document_data.get("document_id", ""),
            "portfolio_summary": {}
        }
        
        # Add metadata
        if "metadata" in document_data:
            portfolio_summary["document_date"] = document_data["metadata"].get("document_date", "")
            portfolio_summary["document_type"] = document_data["metadata"].get("document_type", "")
        
        # Extract portfolio information
        if "financial_data" in document_data and "portfolio" in document_data["financial_data"]:
            portfolio_data = document_data["financial_data"]["portfolio"]
            
            # Summary
            if "summary" in portfolio_data:
                portfolio_summary["portfolio_summary"] = portfolio_data["summary"]
            
            # Securities list
            if "securities" in portfolio_data:
                portfolio_summary["securities"] = portfolio_data["securities"]
        
        # If no portfolio info found, look in general summary
        elif "summary" in document_data and "total_portfolio_value" in document_data["summary"]:
            portfolio_summary["portfolio_summary"]["total_value"] = document_data["summary"]["total_portfolio_value"]
        
        # Export to the requested format
        if not filename:
            filename = f"portfolio_summary_{datetime.now().strftime('%Y%m%d')}"
        
        return self.export_data(portfolio_summary, format_type, filename)
    
    def export_isin_list(self, document_data: Dict[str, Any], format_type: str, filename: Optional[str] = None) -> str:
        """
        Export ISIN list in a dedicated format.
        
        Args:
            document_data: Processed document data
            format_type: Export format
            filename: Optional filename
            
        Returns:
            Path to the created file
        """
        # Create ISIN list data
        isin_data = {
            "extraction_date": datetime.now().isoformat(),
            "document_id": document_data.get("document_id", ""),
            "isin_entities": []
        }
        
        # Extract ISIN entities
        if "entities" in document_data and "isin" in document_data["entities"]:
            isin_data["isin_entities"] = document_data["entities"]["isin"]
        
        # If no dedicated entities found, look in financial data
        elif "financial_data" in document_data and "portfolio" in document_data["financial_data"]:
            securities = document_data["financial_data"]["portfolio"].get("securities", [])
            
            isin_data["isin_entities"] = [
                {"isin": sec.get("isin", ""), "company_name": sec.get("name", sec.get("security_name", ""))}
                for sec in securities if "isin" in sec
            ]
        
        # Export to the requested format
        if not filename:
            filename = f"isin_list_{datetime.now().strftime('%Y%m%d')}"
        
        return self.export_data(isin_data, format_type, filename)
