"""
Entity Relationship Modeler - Models relationships between financial entities.

This module provides tools to extract financial entities and model relationships
between them, such as parent-child relationships, belongs-to relationships, etc.
"""
import os
import re
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
import json
from collections import defaultdict
import networkx as nx

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EntityRelationshipModeler:
    """
    Models relationships between financial entities.
    """
    
    def __init__(self):
        """Initialize the entity relationship modeler."""
        self.entities = {
            "securities": [],
            "asset_classes": [],
            "portfolio": None,
            "structured_products": [],
            "accounts": []
        }
        
        self.relationships = []
        self.entity_graph = nx.DiGraph()
    
    def model(self, extracted_data: Dict[str, Any], output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Model relationships between financial entities.
        
        Args:
            extracted_data: Dictionary containing extracted financial data
            output_dir: Directory to save output files (default: None)
        
        Returns:
            Dict containing entity relationship model
        """
        logger.info("Modeling entity relationships")
        
        # Reset data
        self.entities = {
            "securities": [],
            "asset_classes": [],
            "portfolio": None,
            "structured_products": [],
            "accounts": []
        }
        
        self.relationships = []
        self.entity_graph = nx.DiGraph()
        
        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Extract entities
            self._extract_entities(extracted_data)
            
            # Model relationships
            self._model_relationships()
            
            # Create entity graph
            self._create_entity_graph()
            
            # Save results if output_dir is specified
            if output_dir:
                self._save_results(output_dir)
            
            logger.info("Entity relationship modeling completed.")
            return {
                "entities": self.entities,
                "relationships": self.relationships
            }
            
        except Exception as e:
            logger.error(f"Error modeling entity relationships: {str(e)}")
            return {"error": str(e)}
    
    def _extract_entities(self, extracted_data: Dict[str, Any]):
        """Extract entities from extracted data."""
        # Extract securities
        if "securities" in extracted_data:
            for security in extracted_data["securities"]:
                self.entities["securities"].append({
                    "id": security.get("isin", f"security_{len(self.entities['securities'])}"),
                    "type": "security",
                    "security_type": security.get("security_type", "Unknown"),
                    "description": security.get("description", ""),
                    "valuation": security.get("valuation", None),
                    "data": security
                })
        
        # Extract asset classes
        if "asset_allocation" in extracted_data:
            for asset_allocation in extracted_data["asset_allocation"]:
                asset_class = asset_allocation.get("asset_class", "")
                
                # Skip if empty or already exists
                if not asset_class or any(a["name"] == asset_class for a in self.entities["asset_classes"]):
                    continue
                
                self.entities["asset_classes"].append({
                    "id": f"asset_class_{len(self.entities['asset_classes'])}",
                    "type": "asset_class",
                    "name": asset_class,
                    "value": asset_allocation.get("value", None),
                    "percentage": asset_allocation.get("percentage", None),
                    "data": asset_allocation
                })
        
        # Extract portfolio
        if "portfolio_value" in extracted_data and extracted_data["portfolio_value"]:
            # Find the most frequent portfolio value
            value_counts = defaultdict(int)
            for item in extracted_data["portfolio_value"]:
                value = item["value"]
                value_counts[value] += 1
            
            if value_counts:
                most_frequent_value = max(value_counts.items(), key=lambda x: x[1])[0]
                
                self.entities["portfolio"] = {
                    "id": "portfolio",
                    "type": "portfolio",
                    "value": most_frequent_value,
                    "data": {
                        "value": most_frequent_value,
                        "confidence": value_counts[most_frequent_value] / len(extracted_data["portfolio_value"])
                    }
                }
        
        # Extract structured products
        if "structured_products" in extracted_data:
            for product in extracted_data["structured_products"]:
                self.entities["structured_products"].append({
                    "id": f"structured_product_{len(self.entities['structured_products'])}",
                    "type": "structured_product",
                    "product_type": product.get("type", "Structured Product"),
                    "value": product.get("value", None),
                    "percentage": product.get("percentage", None),
                    "data": product
                })
        
        # Extract accounts
        if "key_value_pairs" in extracted_data:
            for kv_pair in extracted_data["key_value_pairs"]:
                key = kv_pair.get("key", "").lower()
                
                if "account" in key or "cash" in key or "liquidity" in key:
                    self.entities["accounts"].append({
                        "id": f"account_{len(self.entities['accounts'])}",
                        "type": "account",
                        "name": kv_pair.get("key", ""),
                        "value": kv_pair.get("value", None),
                        "currency": kv_pair.get("currency", None),
                        "data": kv_pair
                    })
        
        logger.info(f"Extracted {len(self.entities['securities'])} securities, {len(self.entities['asset_classes'])} asset classes, {len(self.entities['structured_products'])} structured products, and {len(self.entities['accounts'])} accounts")
    
    def _model_relationships(self):
        """Model relationships between entities."""
        # Model portfolio -> asset class relationships
        if self.entities["portfolio"]:
            portfolio_id = self.entities["portfolio"]["id"]
            
            for asset_class in self.entities["asset_classes"]:
                self.relationships.append({
                    "source": portfolio_id,
                    "target": asset_class["id"],
                    "type": "contains",
                    "data": {
                        "value": asset_class.get("value", None),
                        "percentage": asset_class.get("percentage", None)
                    }
                })
        
        # Model asset class -> security relationships
        for security in self.entities["securities"]:
            security_type = security.get("security_type", "").lower()
            
            # Find matching asset class
            matching_asset_class = None
            
            for asset_class in self.entities["asset_classes"]:
                asset_class_name = asset_class["name"].lower()
                
                # Check for direct match
                if security_type in asset_class_name:
                    matching_asset_class = asset_class
                    break
                
                # Check for indirect match
                if (
                    ("bond" in security_type and "bond" in asset_class_name) or
                    ("equity" in security_type and "equity" in asset_class_name) or
                    ("fund" in security_type and "fund" in asset_class_name) or
                    ("structured" in security_type and "structured" in asset_class_name) or
                    ("cash" in security_type and "cash" in asset_class_name)
                ):
                    matching_asset_class = asset_class
                    break
            
            if matching_asset_class:
                self.relationships.append({
                    "source": matching_asset_class["id"],
                    "target": security["id"],
                    "type": "contains",
                    "data": {
                        "value": security.get("valuation", None)
                    }
                })
            elif self.entities["portfolio"]:
                # If no matching asset class, link directly to portfolio
                self.relationships.append({
                    "source": self.entities["portfolio"]["id"],
                    "target": security["id"],
                    "type": "contains",
                    "data": {
                        "value": security.get("valuation", None)
                    }
                })
        
        # Model structured product relationships
        for product in self.entities["structured_products"]:
            product_type = product.get("product_type", "").lower()
            
            # Find matching asset class
            matching_asset_class = None
            
            for asset_class in self.entities["asset_classes"]:
                asset_class_name = asset_class["name"].lower()
                
                if "structured" in asset_class_name:
                    matching_asset_class = asset_class
                    break
            
            if matching_asset_class:
                self.relationships.append({
                    "source": matching_asset_class["id"],
                    "target": product["id"],
                    "type": "contains",
                    "data": {
                        "value": product.get("value", None),
                        "percentage": product.get("percentage", None)
                    }
                })
            elif self.entities["portfolio"]:
                # If no matching asset class, link directly to portfolio
                self.relationships.append({
                    "source": self.entities["portfolio"]["id"],
                    "target": product["id"],
                    "type": "contains",
                    "data": {
                        "value": product.get("value", None),
                        "percentage": product.get("percentage", None)
                    }
                })
        
        # Model account relationships
        for account in self.entities["accounts"]:
            # Find matching asset class (usually liquidity or cash)
            matching_asset_class = None
            
            for asset_class in self.entities["asset_classes"]:
                asset_class_name = asset_class["name"].lower()
                
                if "cash" in asset_class_name or "liquidity" in asset_class_name:
                    matching_asset_class = asset_class
                    break
            
            if matching_asset_class:
                self.relationships.append({
                    "source": matching_asset_class["id"],
                    "target": account["id"],
                    "type": "contains",
                    "data": {
                        "value": account.get("value", None)
                    }
                })
            elif self.entities["portfolio"]:
                # If no matching asset class, link directly to portfolio
                self.relationships.append({
                    "source": self.entities["portfolio"]["id"],
                    "target": account["id"],
                    "type": "contains",
                    "data": {
                        "value": account.get("value", None)
                    }
                })
        
        # Model parent-child relationships between asset classes
        self._model_asset_class_hierarchy()
        
        logger.info(f"Modeled {len(self.relationships)} relationships")
    
    def _model_asset_class_hierarchy(self):
        """Model parent-child relationships between asset classes."""
        # Create a copy of asset classes for processing
        asset_classes = list(self.entities["asset_classes"])
        
        # Sort by name length (shorter names are likely parent classes)
        asset_classes.sort(key=lambda x: len(x["name"]))
        
        # Track processed asset classes
        processed = set()
        
        # Process each asset class
        for i, parent in enumerate(asset_classes):
            if parent["id"] in processed:
                continue
            
            parent_name = parent["name"].lower()
            processed.add(parent["id"])
            
            # Look for potential child asset classes
            for j, child in enumerate(asset_classes):
                if i == j or child["id"] in processed:
                    continue
                
                child_name = child["name"].lower()
                
                # Check if child name contains parent name
                if parent_name in child_name and len(child_name) > len(parent_name):
                    # This is likely a parent-child relationship
                    self.relationships.append({
                        "source": parent["id"],
                        "target": child["id"],
                        "type": "parent_of",
                        "data": {}
                    })
                    
                    processed.add(child["id"])
    
    def _create_entity_graph(self):
        """Create a directed graph of entity relationships."""
        # Add entities as nodes
        for entity_type, entities in self.entities.items():
            if entity_type == "portfolio":
                if entities:
                    self.entity_graph.add_node(
                        entities["id"],
                        type=entities["type"],
                        value=entities["value"],
                        data=entities["data"]
                    )
            else:
                for entity in entities:
                    self.entity_graph.add_node(
                        entity["id"],
                        type=entity["type"],
                        data=entity
                    )
        
        # Add relationships as edges
        for relationship in self.relationships:
            self.entity_graph.add_edge(
                relationship["source"],
                relationship["target"],
                type=relationship["type"],
                data=relationship["data"]
            )
        
        logger.info(f"Created entity graph with {self.entity_graph.number_of_nodes()} nodes and {self.entity_graph.number_of_edges()} edges")
    
    def _save_results(self, output_dir):
        """Save modeling results."""
        # Save entities and relationships as JSON
        model_path = os.path.join(output_dir, "entity_relationship_model.json")
        
        model_data = {
            "entities": self.entities,
            "relationships": self.relationships
        }
        
        with open(model_path, "w", encoding="utf-8") as f:
            json.dump(model_data, f, indent=2)
        
        # Save graph as GraphML if networkx is available
        try:
            graph_path = os.path.join(output_dir, "entity_graph.graphml")
            nx.write_graphml(self.entity_graph, graph_path)
        except Exception as e:
            logger.warning(f"Error saving graph: {str(e)}")
        
        logger.info(f"Saved modeling results to {output_dir}")
    
    def get_entity_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an entity by its ID.
        
        Args:
            entity_id: ID of the entity to retrieve
        
        Returns:
            Entity data or None if not found
        """
        # Check portfolio
        if self.entities["portfolio"] and self.entities["portfolio"]["id"] == entity_id:
            return self.entities["portfolio"]
        
        # Check other entity types
        for entity_type in ["securities", "asset_classes", "structured_products", "accounts"]:
            for entity in self.entities[entity_type]:
                if entity["id"] == entity_id:
                    return entity
        
        return None
    
    def get_relationships_by_entity_id(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        Get relationships involving a specific entity.
        
        Args:
            entity_id: ID of the entity
        
        Returns:
            List of relationships involving the entity
        """
        return [r for r in self.relationships if r["source"] == entity_id or r["target"] == entity_id]
    
    def get_children(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        Get child entities of a specific entity.
        
        Args:
            entity_id: ID of the parent entity
        
        Returns:
            List of child entities
        """
        child_ids = [r["target"] for r in self.relationships if r["source"] == entity_id]
        return [self.get_entity_by_id(child_id) for child_id in child_ids if self.get_entity_by_id(child_id)]
    
    def get_parents(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        Get parent entities of a specific entity.
        
        Args:
            entity_id: ID of the child entity
        
        Returns:
            List of parent entities
        """
        parent_ids = [r["source"] for r in self.relationships if r["target"] == entity_id]
        return [self.get_entity_by_id(parent_id) for parent_id in parent_ids if self.get_entity_by_id(parent_id)]
    
    def get_entity_hierarchy(self, entity_id: str) -> Dict[str, Any]:
        """
        Get the hierarchy of an entity (parents and children).
        
        Args:
            entity_id: ID of the entity
        
        Returns:
            Dict containing the entity, its parents, and its children
        """
        entity = self.get_entity_by_id(entity_id)
        if not entity:
            return {"error": f"Entity not found: {entity_id}"}
        
        parents = self.get_parents(entity_id)
        children = self.get_children(entity_id)
        
        return {
            "entity": entity,
            "parents": parents,
            "children": children
        }
    
    def get_portfolio_structure(self) -> Dict[str, Any]:
        """
        Get the complete portfolio structure.
        
        Returns:
            Dict containing the portfolio structure
        """
        if not self.entities["portfolio"]:
            return {"error": "Portfolio not found"}
        
        portfolio = self.entities["portfolio"]
        
        # Get top-level asset classes
        top_level_asset_classes = []
        
        for asset_class in self.entities["asset_classes"]:
            parents = self.get_parents(asset_class["id"])
            
            # Check if this asset class has the portfolio as parent
            if any(p["id"] == portfolio["id"] for p in parents):
                # Get children of this asset class
                children = self.get_children(asset_class["id"])
                
                asset_class_with_children = dict(asset_class)
                asset_class_with_children["children"] = children
                
                top_level_asset_classes.append(asset_class_with_children)
        
        # Get securities not belonging to any asset class
        orphan_securities = []
        
        for security in self.entities["securities"]:
            parents = self.get_parents(security["id"])
            
            # Check if this security has the portfolio as parent
            if any(p["id"] == portfolio["id"] for p in parents):
                orphan_securities.append(security)
        
        return {
            "portfolio": portfolio,
            "asset_classes": top_level_asset_classes,
            "orphan_securities": orphan_securities
        }

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Model relationships between financial entities.")
    parser.add_argument("file_path", help="Path to the extracted data JSON file")
    parser.add_argument("--output-dir", help="Directory to save output files")
    
    args = parser.parse_args()
    
    # Check if the file exists
    if not os.path.exists(args.file_path):
        logger.error(f"Error: File not found: {args.file_path}")
        return 1
    
    # Read the extracted data
    with open(args.file_path, "r", encoding="utf-8") as f:
        extracted_data = json.load(f)
    
    # Model entity relationships
    modeler = EntityRelationshipModeler()
    result = modeler.model(extracted_data, output_dir=args.output_dir)
    
    # Print summary
    print("\nEntity Relationship Modeling Summary:")
    print("===================================")
    
    print(f"Securities: {len(result['entities']['securities'])}")
    print(f"Asset Classes: {len(result['entities']['asset_classes'])}")
    print(f"Structured Products: {len(result['entities']['structured_products'])}")
    print(f"Accounts: {len(result['entities']['accounts'])}")
    print(f"Relationships: {len(result['relationships'])}")
    
    # Print portfolio structure
    portfolio_structure = modeler.get_portfolio_structure()
    if "error" not in portfolio_structure:
        print("\nPortfolio Structure:")
        print(f"Portfolio Value: {portfolio_structure['portfolio']['value']:,.2f}")
        
        print("\nTop-Level Asset Classes:")
        for asset_class in portfolio_structure['asset_classes']:
            print(f"- {asset_class['name']}: {asset_class['value']:,.2f} ({asset_class['percentage']}%)")
            
            if asset_class['children']:
                for child in asset_class['children']:
                    if child['type'] == 'asset_class':
                        print(f"  - {child['name']}: {child['value']:,.2f} ({child['percentage']}%)")
    
    return 0

if __name__ == "__main__":
    main()
