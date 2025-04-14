"""
Document Comparison Agent for comparing documents and identifying changes.
"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
import uuid
from .base_agent import BaseAgent

class DocumentComparisonAgent(BaseAgent):
    """Agent for comparing documents and identifying changes and developments."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the document comparison agent.
        
        Args:
            api_key: OpenRouter API key
            **kwargs: Additional parameters for the base agent
        """
        super().__init__(name="Document Comparison Agent")
        self.api_key = api_key
        self.description = "I compare documents and identify changes and developments."
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task to compare documents.
        
        Args:
            task: Task dictionary with the following keys:
                - current_doc: Current document data
                - previous_doc: Previous document data
                
        Returns:
            Dictionary with comparison results
        """
        # Get the required data
        current_doc = task.get('current_doc', {})
        previous_doc = task.get('previous_doc', {})
        
        # Check if we have both documents
        if not current_doc or not previous_doc:
            return {
                'status': 'error',
                'message': 'Both current and previous documents are required for comparison'
            }
        
        # Perform the comparison
        try:
            comparison_result = self.compare_documents(current_doc, previous_doc)
            
            return {
                'status': 'success',
                'comparison_result': comparison_result
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error comparing documents: {str(e)}'
            }
    
    def compare_documents(self, current_doc: Dict[str, Any], previous_doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare two documents and identify changes.
        
        Args:
            current_doc: Current document
            previous_doc: Previous document
            
        Returns:
            Dictionary with comparison results
        """
        comparison_result = {
            "comparison_id": str(uuid.uuid4()),
            "comparison_date": datetime.now().isoformat(),
            "current_document_id": current_doc.get("document_id", ""),
            "previous_document_id": previous_doc.get("document_id", ""),
            "metadata_comparison": self._compare_metadata(current_doc, previous_doc),
            "portfolio_comparison": self._compare_portfolio(current_doc, previous_doc),
            "isin_comparison": self._compare_isin_entities(current_doc, previous_doc),
            "tables_comparison": self._compare_tables(current_doc, previous_doc),
            "summary": {
                "significant_changes": []
            }
        }
        
        # Extract significant changes
        comparison_result["summary"]["significant_changes"] = self._extract_significant_changes(comparison_result)
        
        return comparison_result
    
    def _compare_metadata(self, current_doc: Dict[str, Any], previous_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Compare metadata between two documents."""
        comparison = {
            "fields_compared": [],
            "changed_fields": [],
            "changes": {}
        }
        
        # Ensure both documents have metadata
        if "metadata" not in current_doc or "metadata" not in previous_doc:
            return comparison
        
        current_metadata = current_doc["metadata"]
        previous_metadata = previous_doc["metadata"]
        
        # Compare common fields
        all_fields = set(current_metadata.keys()) | set(previous_metadata.keys())
        comparison["fields_compared"] = list(all_fields)
        
        for field in all_fields:
            current_value = current_metadata.get(field)
            previous_value = previous_metadata.get(field)
            
            # Check for change
            if current_value != previous_value:
                comparison["changed_fields"].append(field)
                comparison["changes"][field] = {
                    "previous": previous_value,
                    "current": current_value
                }
        
        return comparison
    
    def _compare_portfolio(self, current_doc: Dict[str, Any], previous_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Compare portfolio data between two documents."""
        comparison = {
            "total_value_change": None,
            "total_value_change_percent": None,
            "security_changes": [],
            "new_securities": [],
            "removed_securities": [],
            "type_distribution_changes": {}
        }
        
        # Extract portfolio data from documents
        current_portfolio = self._extract_portfolio_data(current_doc)
        previous_portfolio = self._extract_portfolio_data(previous_doc)
        
        if not current_portfolio or not previous_portfolio:
            return comparison
        
        # Compare total value
        if "total_value" in current_portfolio and "total_value" in previous_portfolio:
            current_value = current_portfolio["total_value"]
            previous_value = previous_portfolio["total_value"]
            
            value_change = current_value - previous_value
            value_change_percent = (value_change / previous_value) * 100 if previous_value != 0 else 0
            
            comparison["total_value_change"] = value_change
            comparison["total_value_change_percent"] = value_change_percent
        
        # Compare securities
        if "securities" in current_portfolio and "securities" in previous_portfolio:
            current_securities = {sec.get("isin", i): sec for i, sec in enumerate(current_portfolio["securities"])}
            previous_securities = {sec.get("isin", i): sec for i, sec in enumerate(previous_portfolio["securities"])}
            
            # Find new securities
            new_isin_codes = set(current_securities.keys()) - set(previous_securities.keys())
            for isin in new_isin_codes:
                if isinstance(isin, str):  # Only if it's actually an ISIN and not an index
                    comparison["new_securities"].append(current_securities[isin])
            
            # Find removed securities
            removed_isin_codes = set(previous_securities.keys()) - set(current_securities.keys())
            for isin in removed_isin_codes:
                if isinstance(isin, str):  # Only if it's actually an ISIN and not an index
                    comparison["removed_securities"].append(previous_securities[isin])
            
            # Compare common securities
            common_isin_codes = set(current_securities.keys()) & set(previous_securities.keys())
            for isin in common_isin_codes:
                if not isinstance(isin, str):  # Skip indices
                    continue
                    
                current_sec = current_securities[isin]
                previous_sec = previous_securities[isin]
                
                changes = {}
                
                # Compare all common fields
                all_fields = set(current_sec.keys()) | set(previous_sec.keys())
                for field in all_fields:
                    current_value = current_sec.get(field)
                    previous_value = previous_sec.get(field)
                    
                    # Check for change
                    if current_value != previous_value:
                        # Calculate percent change for numeric values
                        percent_change = None
                        if isinstance(current_value, (int, float)) and isinstance(previous_value, (int, float)) and previous_value != 0:
                            percent_change = ((current_value - previous_value) / abs(previous_value)) * 100
                        
                        changes[field] = {
                            "previous": previous_value,
                            "current": current_value,
                            "change": current_value - previous_value if isinstance(current_value, (int, float)) and isinstance(previous_value, (int, float)) else None,
                            "percent_change": percent_change
                        }
                
                if changes:
                    comparison["security_changes"].append({
                        "isin": isin,
                        "security_name": current_sec.get("name", current_sec.get("security_name", "")),
                        "changes": changes
                    })
        
        # Compare type distribution
        if "type_distribution" in current_portfolio and "type_distribution" in previous_portfolio:
            current_dist = current_portfolio["type_distribution"]
            previous_dist = previous_portfolio["type_distribution"]
            
            all_types = set(current_dist.keys()) | set(previous_dist.keys())
            for sec_type in all_types:
                current_value = current_dist.get(sec_type, 0)
                previous_value = previous_dist.get(sec_type, 0)
                
                if current_value != previous_value:
                    value_change = current_value - previous_value
                    percent_change = (value_change / previous_value) * 100 if previous_value != 0 else 0
                    
                    comparison["type_distribution_changes"][sec_type] = {
                        "previous": previous_value,
                        "current": current_value,
                        "change": value_change,
                        "percent_change": percent_change
                    }
        
        return comparison
    
    def _compare_isin_entities(self, current_doc: Dict[str, Any], previous_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Compare ISIN entities between two documents."""
        comparison = {
            "new_entities": [],
            "removed_entities": [],
            "changed_entities": []
        }
        
        # Extract ISIN entities from documents
        current_entities = self._extract_isin_entities(current_doc)
        previous_entities = self._extract_isin_entities(previous_doc)
        
        if not current_entities or not previous_entities:
            return comparison
        
        # Map by ISIN
        current_isin_map = {entity.get("isin", ""): entity for entity in current_entities if "isin" in entity}
        previous_isin_map = {entity.get("isin", ""): entity for entity in previous_entities if "isin" in entity}
        
        # Find new entities
        new_isin_codes = set(current_isin_map.keys()) - set(previous_isin_map.keys())
        for isin in new_isin_codes:
            comparison["new_entities"].append(current_isin_map[isin])
        
        # Find removed entities
        removed_isin_codes = set(previous_isin_map.keys()) - set(current_isin_map.keys())
        for isin in removed_isin_codes:
            comparison["removed_entities"].append(previous_isin_map[isin])
        
        # Compare common entities
        common_isin_codes = set(current_isin_map.keys()) & set(previous_isin_map.keys())
        for isin in common_isin_codes:
            current_entity = current_isin_map[isin]
            previous_entity = previous_isin_map[isin]
            
            changes = {}
            
            # Compare all common fields
            all_fields = set(current_entity.keys()) | set(previous_entity.keys())
            for field in all_fields:
                if field == "isin":  # Skip the ISIN field itself
                    continue
                    
                current_value = current_entity.get(field)
                previous_value = previous_entity.get(field)
                
                # Check for change
                if current_value != previous_value:
                    changes[field] = {
                        "previous": previous_value,
                        "current": current_value
                    }
            
            if changes:
                comparison["changed_entities"].append({
                    "isin": isin,
                    "changes": changes
                })
        
        return comparison
    
    def _compare_tables(self, current_doc: Dict[str, Any], previous_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Compare tables between two documents."""
        comparison = {
            "tables_compared": [],
            "table_changes": {}
        }
        
        # Ensure both documents have tables
        if "tables" not in current_doc or "tables" not in previous_doc:
            return comparison
        
        current_tables = current_doc["tables"]
        previous_tables = previous_doc["tables"]
        
        # Map tables by type
        current_tables_by_type = {}
        for table in current_tables:
            table_type = table.get("type", "unknown")
            if table_type not in current_tables_by_type:
                current_tables_by_type[table_type] = []
            current_tables_by_type[table_type].append(table)
            
        previous_tables_by_type = {}
        for table in previous_tables:
            table_type = table.get("type", "unknown")
            if table_type not in previous_tables_by_type:
                previous_tables_by_type[table_type] = []
            previous_tables_by_type[table_type].append(table)
        
        # Compare tables of the same type
        common_types = set(current_tables_by_type.keys()) & set(previous_tables_by_type.keys())
        comparison["tables_compared"] = list(common_types)
        
        for table_type in common_types:
            comparison["table_changes"][table_type] = []
            
            # Select the first table of each type for simplicity
            # This could be expanded to do more complex matching between tables
            current_table = current_tables_by_type[table_type][0]
            previous_table = previous_tables_by_type[table_type][0]
            
            # Compare table data
            if "data" in current_table and "data" in previous_table:
                current_data = current_table["data"]
                previous_data = previous_table["data"]
                
                # Try to find a key field (e.g., ISIN)
                key_field = self._find_key_field(current_data, previous_data)
                
                if key_field:
                    # Compare by key field
                    table_changes = self._compare_table_data_by_key(current_data, previous_data, key_field)
                else:
                    # Compare by position
                    table_changes = self._compare_table_data_by_position(current_data, previous_data)
                
                comparison["table_changes"][table_type] = table_changes
        
        return comparison
    
    def _extract_portfolio_data(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Extract portfolio data from a document."""
        portfolio_data = {}
        
        # Look in financial data
        if "financial_data" in document and "portfolio" in document["financial_data"]:
            portfolio = document["financial_data"]["portfolio"]
            
            # Summary
            if "summary" in portfolio:
                portfolio_data.update(portfolio["summary"])
            
            # Securities list
            if "securities" in portfolio:
                portfolio_data["securities"] = portfolio["securities"]
                
                # Calculate summaries
                if "securities" in portfolio_data:
                    securities = portfolio_data["securities"]
                    total_value = sum(sec.get("value", 0) for sec in securities 
                                   if isinstance(sec.get("value", 0), (int, float)))
                    
                    portfolio_data["total_value"] = total_value
        
        # If no portfolio info found, look in general summary
        elif "summary" in document and "total_portfolio_value" in document["summary"]:
            portfolio_data["total_value"] = document["summary"]["total_portfolio_value"]
        
        # Look in tables
        elif "tables" in document:
            for table in document["tables"]:
                if table.get("type") == "portfolio" and "data" in table:
                    # Create securities list from table
                    securities = []
                    
                    for row in table["data"]:
                        security = {}
                        
                        # Look for common fields
                        for key, value in row.items():
                            key_lower = str(key).lower()
                            
                            # Security name
                            if "name" in key_lower or "description" in key_lower:
                                security["name"] = value
                            # ISIN
                            elif "isin" in key_lower:
                                security["isin"] = value
                            # Security type
                            elif "type" in key_lower:
                                security["type"] = value
                            # Quantity
                            elif "quantity" in key_lower or "amount" in key_lower:
                                security["quantity"] = self._parse_numeric(value)
                            # Price
                            elif "price" in key_lower or "rate" in key_lower:
                                security["price"] = self._parse_numeric(value)
                            # Value
                            elif "value" in key_lower or "total" in key_lower:
                                security["value"] = self._parse_numeric(value)
                            # Return
                            elif "return" in key_lower or "yield" in key_lower:
                                security["return"] = self._parse_numeric(value)
                        
                        if security:
                            securities.append(security)
                    
                    if securities:
                        portfolio_data["securities"] = securities
                        
                        # Calculate summaries
                        total_value = sum(sec.get("value", 0) for sec in securities 
                                       if isinstance(sec.get("value", 0), (int, float)))
                        
                        portfolio_data["total_value"] = total_value
                        
                        break
        
        return portfolio_data
    
    def _extract_isin_entities(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract ISIN entities from a document."""
        # Look in entities
        if "entities" in document and "isin" in document["entities"]:
            return document["entities"]["isin"]
        
        # Look in financial data
        if "financial_data" in document and "portfolio" in document["financial_data"]:
            securities = document["financial_data"]["portfolio"].get("securities", [])
            
            # Filter only securities with ISIN
            return [sec for sec in securities if "isin" in sec]
        
        return []
    
    def _find_key_field(self, current_data: List[Dict[str, Any]], previous_data: List[Dict[str, Any]]) -> Optional[str]:
        """Find a possible key field for a table."""
        if not current_data or not previous_data:
            return None
            
        # Candidate key fields
        key_candidates = ["isin", "id", "code", "number"]
        
        # Check fields
        common_fields = set(current_data[0].keys()) & set(previous_data[0].keys())
        
        for field in key_candidates:
            if any(field in key.lower() for key in common_fields):
                matching_field = next((key for key in common_fields if field in key.lower()), None)
                if matching_field:
                    return matching_field
        
        return None
    
    def _compare_table_data_by_key(self, current_data: List[Dict[str, Any]], previous_data: List[Dict[str, Any]], key_field: str) -> List[Dict[str, Any]]:
        """Compare table data by key field."""
        changes = []
        
        # Map rows by key
        current_map = {row.get(key_field, i): row for i, row in enumerate(current_data)}
        previous_map = {row.get(key_field, i): row for i, row in enumerate(previous_data)}
        
        # Find new keys
        new_keys = set(current_map.keys()) - set(previous_map.keys())
        for key in new_keys:
            if isinstance(key, str):  # Only if it's actually a key and not an index
                changes.append({
                    "key": key,
                    "type": "added",
                    "data": current_map[key]
                })
        
        # Find removed keys
        removed_keys = set(previous_map.keys()) - set(current_map.keys())
        for key in removed_keys:
            if isinstance(key, str):  # Only if it's actually a key and not an index
                changes.append({
                    "key": key,
                    "type": "removed",
                    "data": previous_map[key]
                })
        
        # Compare common rows
        common_keys = set(current_map.keys()) & set(previous_map.keys())
        for key in common_keys:
            if not isinstance(key, str):  # Skip indices
                continue
                
            current_row = current_map[key]
            previous_row = previous_map[key]
            
            field_changes = {}
            
            # Compare all common fields
            all_fields = set(current_row.keys()) | set(previous_row.keys())
            for field in all_fields:
                if field == key_field:  # Skip the key field itself
                    continue
                    
                current_value = current_row.get(field)
                previous_value = previous_row.get(field)
                
                # Check for change
                if current_value != previous_value:
                    # Calculate percent change for numeric values
                    percent_change = None
                    if isinstance(current_value, (int, float)) and isinstance(previous_value, (int, float)) and previous_value != 0:
                        percent_change = ((current_value - previous_value) / abs(previous_value)) * 100
                    
                    field_changes[field] = {
                        "previous": previous_value,
                        "current": current_value,
                        "change": current_value - previous_value if isinstance(current_value, (int, float)) and isinstance(previous_value, (int, float)) else None,
                        "percent_change": percent_change
                    }
            
            if field_changes:
                changes.append({
                    "key": key,
                    "type": "modified",
                    "changes": field_changes
                })
        
        return changes
    
    def _compare_table_data_by_position(self, current_data: List[Dict[str, Any]], previous_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Compare table data by position (index)."""
        changes = []
        
        # Compare row count
        if len(current_data) != len(previous_data):
            changes.append({
                "type": "row_count_changed",
                "previous_count": len(previous_data),
                "current_count": len(current_data)
            })
        
        # Compare rows by position
        for i in range(min(len(current_data), len(previous_data))):
            current_row = current_data[i]
            previous_row = previous_data[i]
            
            field_changes = {}
            
            # Compare all common fields
            all_fields = set(current_row.keys()) | set(previous_row.keys())
            for field in all_fields:
                current_value = current_row.get(field)
                previous_value = previous_row.get(field)
                
                # Check for change
                if current_value != previous_value:
                    # Calculate percent change for numeric values
                    percent_change = None
                    if isinstance(current_value, (int, float)) and isinstance(previous_value, (int, float)) and previous_value != 0:
                        percent_change = ((current_value - previous_value) / abs(previous_value)) * 100
                    
                    field_changes[field] = {
                        "previous": previous_value,
                        "current": current_value,
                        "change": current_value - previous_value if isinstance(current_value, (int, float)) and isinstance(previous_value, (int, float)) else None,
                        "percent_change": percent_change
                    }
            
            if field_changes:
                changes.append({
                    "index": i,
                    "type": "modified",
                    "changes": field_changes
                })
        
        # Handle new rows
        if len(current_data) > len(previous_data):
            for i in range(len(previous_data), len(current_data)):
                changes.append({
                    "index": i,
                    "type": "added",
                    "data": current_data[i]
                })
        
        # Handle removed rows
        if len(previous_data) > len(current_data):
            for i in range(len(current_data), len(previous_data)):
                changes.append({
                    "index": i,
                    "type": "removed",
                    "data": previous_data[i]
                })
        
        return changes
    
    def _extract_significant_changes(self, comparison_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract significant changes from comparison results."""
        significant_changes = []
        
        # Portfolio value change
        if "portfolio_comparison" in comparison_result:
            portfolio_comp = comparison_result["portfolio_comparison"]
            
            if portfolio_comp.get("total_value_change_percent") is not None:
                change_percent = portfolio_comp["total_value_change_percent"]
                
                # Significant portfolio value change (more than 5%)
                if abs(change_percent) >= 5:
                    direction = "increase" if change_percent > 0 else "decrease"
                    significant_changes.append({
                        "type": "portfolio_value",
                        "description": f"{direction} of {abs(change_percent):.2f}% in portfolio value",
                        "change_percent": change_percent,
                        "change_value": portfolio_comp.get("total_value_change")
                    })
            
            # New securities
            if portfolio_comp.get("new_securities"):
                significant_changes.append({
                    "type": "new_securities",
                    "description": f"Added {len(portfolio_comp['new_securities'])} new securities to the portfolio",
                    "count": len(portfolio_comp["new_securities"]),
                    "securities": portfolio_comp["new_securities"]
                })
            
            # Removed securities
            if portfolio_comp.get("removed_securities"):
                significant_changes.append({
                    "type": "removed_securities",
                    "description": f"Removed {len(portfolio_comp['removed_securities'])} securities from the portfolio",
                    "count": len(portfolio_comp["removed_securities"]),
                    "securities": portfolio_comp["removed_securities"]
                })
            
            # Significant changes in specific securities
            if portfolio_comp.get("security_changes"):
                for security_change in portfolio_comp["security_changes"]:
                    changes = security_change.get("changes", {})
                    
                    # Look for significant percent changes
                    for field, change_data in changes.items():
                        if change_data.get("percent_change") is not None and abs(change_data["percent_change"]) >= 10:
                            direction = "increase" if change_data["percent_change"] > 0 else "decrease"
                            significant_changes.append({
                                "type": "security_field_change",
                                "security_name": security_change.get("security_name", ""),
                                "isin": security_change.get("isin", ""),
                                "field": field,
                                "description": f"{direction} of {abs(change_data['percent_change']):.2f}% in {field} of {security_change.get('security_name', '')}",
                                "change_percent": change_data["percent_change"],
                                "previous_value": change_data["previous"],
                                "current_value": change_data["current"]
                            })
        
        return significant_changes
    
    def _parse_numeric(self, value) -> Optional[float]:
        """Parse a value to a number."""
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Remove non-numeric characters
            import re
            clean_val = re.sub(r'[^\d.-]', '', value.replace(',', ''))
            
            try:
                return float(clean_val)
            except (ValueError, TypeError):
                pass
        
        return None
