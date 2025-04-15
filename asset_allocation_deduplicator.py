"""
Asset Allocation Deduplicator - Deduplicates asset allocation entries.

This module provides tools to deduplicate asset allocation entries and
reconcile asset allocation percentages.
"""
import os
import re
import logging
from typing import Dict, List, Any, Optional, Tuple, Set, Union
import json
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AssetAllocationDeduplicator:
    """
    Deduplicates asset allocation entries and reconciles asset allocation percentages.
    """
    
    def __init__(self):
        """Initialize the asset allocation deduplicator."""
        self.asset_allocations = []
        self.deduplicated_allocations = []
        self.normalized_allocations = []
    
    def deduplicate(self, asset_allocations: List[Dict[str, Any]], output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Deduplicate asset allocation entries.
        
        Args:
            asset_allocations: List of asset allocation entries
            output_dir: Directory to save output files (default: None)
        
        Returns:
            Dict containing deduplicated and normalized asset allocations
        """
        logger.info("Deduplicating asset allocation entries")
        
        # Reset data
        self.asset_allocations = asset_allocations
        self.deduplicated_allocations = []
        self.normalized_allocations = []
        
        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Deduplicate asset allocations
            self._deduplicate_allocations()
            
            # Normalize asset allocation percentages
            self._normalize_percentages()
            
            # Save results if output_dir is specified
            if output_dir:
                self._save_results(output_dir)
            
            logger.info("Asset allocation deduplication completed.")
            return {
                "original_allocations": self.asset_allocations,
                "deduplicated_allocations": self.deduplicated_allocations,
                "normalized_allocations": self.normalized_allocations
            }
            
        except Exception as e:
            logger.error(f"Error deduplicating asset allocations: {str(e)}")
            return {"error": str(e)}
    
    def _clean_asset_class(self, asset_class: str) -> str:
        """Clean asset class name."""
        # Remove leading/trailing whitespace
        cleaned = asset_class.strip()
        
        # Remove leading/trailing punctuation
        cleaned = re.sub(r'^[^\w]+|[^\w]+$', '', cleaned)
        
        # Convert to lowercase
        cleaned = cleaned.lower()
        
        return cleaned
    
    def _deduplicate_allocations(self):
        """Deduplicate asset allocation entries."""
        if not self.asset_allocations:
            return
        
        # Group allocations by cleaned asset class
        allocations_by_class = defaultdict(list)
        
        for allocation in self.asset_allocations:
            asset_class = allocation.get("asset_class", "")
            if not asset_class:
                continue
            
            cleaned_class = self._clean_asset_class(asset_class)
            allocations_by_class[cleaned_class].append(allocation)
        
        # Deduplicate
        for cleaned_class, allocations in allocations_by_class.items():
            if len(allocations) == 1:
                # Only one allocation with this asset class
                self.deduplicated_allocations.append(allocations[0])
            else:
                # Multiple allocations with the same asset class
                # Merge them
                merged = self._merge_allocations(allocations)
                self.deduplicated_allocations.append(merged)
        
        logger.info(f"Deduplicated {len(self.asset_allocations)} allocations to {len(self.deduplicated_allocations)} unique allocations")
    
    def _merge_allocations(self, allocations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge multiple allocations with the same asset class."""
        if not allocations:
            return {}
        
        # Use the first allocation as a base
        merged = dict(allocations[0])
        
        # Track sources
        merged["sources"] = [
            {
                "value": allocation.get("value"),
                "percentage": allocation.get("percentage"),
                "source": allocation.get("source", "unknown"),
                "extraction_method": allocation.get("extraction_method", "unknown")
            }
            for allocation in allocations
        ]
        
        # Use the most common asset class name
        asset_class_counts = defaultdict(int)
        for allocation in allocations:
            asset_class = allocation.get("asset_class", "")
            if asset_class:
                asset_class_counts[asset_class] += 1
        
        if asset_class_counts:
            merged["asset_class"] = max(asset_class_counts.items(), key=lambda x: x[1])[0]
        
        # Use the median value and percentage
        values = [allocation.get("value") for allocation in allocations if allocation.get("value") is not None]
        percentages = [allocation.get("percentage") for allocation in allocations if allocation.get("percentage") is not None]
        
        if values:
            values.sort()
            if len(values) % 2 == 0:
                merged["value"] = (values[len(values) // 2 - 1] + values[len(values) // 2]) / 2
            else:
                merged["value"] = values[len(values) // 2]
        
        if percentages:
            percentages.sort()
            if len(percentages) % 2 == 0:
                merged["percentage"] = (percentages[len(percentages) // 2 - 1] + percentages[len(percentages) // 2]) / 2
            else:
                merged["percentage"] = percentages[len(percentages) // 2]
        
        return merged
    
    def _normalize_percentages(self):
        """Normalize asset allocation percentages to sum to 100%."""
        if not self.deduplicated_allocations:
            return
        
        # Filter out total rows
        non_total_allocations = [a for a in self.deduplicated_allocations if not a.get("is_total", False)]
        
        # Calculate total percentage
        total_percentage = sum(a.get("percentage", 0) or 0 for a in non_total_allocations)
        
        # Normalize percentages
        if total_percentage > 0:
            for allocation in non_total_allocations:
                normalized = dict(allocation)
                
                if "percentage" in normalized and normalized["percentage"] is not None:
                    normalized["original_percentage"] = normalized["percentage"]
                    normalized["percentage"] = (normalized["percentage"] / total_percentage) * 100
                
                self.normalized_allocations.append(normalized)
        else:
            # If no percentages, just copy the deduplicated allocations
            self.normalized_allocations = list(self.deduplicated_allocations)
        
        logger.info(f"Normalized {len(self.normalized_allocations)} asset allocations")
    
    def _save_results(self, output_dir):
        """Save deduplication results."""
        # Save deduplicated allocations as JSON
        deduplicated_path = os.path.join(output_dir, "deduplicated_allocations.json")
        with open(deduplicated_path, "w", encoding="utf-8") as f:
            json.dump(self.deduplicated_allocations, f, indent=2)
        
        # Save normalized allocations as JSON
        normalized_path = os.path.join(output_dir, "normalized_allocations.json")
        with open(normalized_path, "w", encoding="utf-8") as f:
            json.dump(self.normalized_allocations, f, indent=2)
        
        logger.info(f"Saved deduplication results to {output_dir}")
    
    def get_deduplicated_allocations(self) -> List[Dict[str, Any]]:
        """
        Get deduplicated asset allocations.
        
        Returns:
            List of deduplicated asset allocations
        """
        return self.deduplicated_allocations
    
    def get_normalized_allocations(self) -> List[Dict[str, Any]]:
        """
        Get normalized asset allocations.
        
        Returns:
            List of normalized asset allocations
        """
        return self.normalized_allocations
    
    def get_top_asset_classes(self, n: int = 5) -> List[Dict[str, Any]]:
        """
        Get the top N asset classes by percentage.
        
        Args:
            n: Number of asset classes to retrieve (default: 5)
        
        Returns:
            List of top N asset classes by percentage
        """
        # Filter allocations with percentage
        allocations_with_percentage = [a for a in self.normalized_allocations if a.get("percentage")]
        
        # Sort by percentage (descending)
        sorted_allocations = sorted(allocations_with_percentage, key=lambda a: a["percentage"], reverse=True)
        
        return sorted_allocations[:n]
    
    def get_asset_allocation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of asset allocations.
        
        Returns:
            Dict containing asset allocation summary
        """
        if not self.normalized_allocations:
            return {
                "total_percentage": 0,
                "asset_classes": 0,
                "top_classes": []
            }
        
        # Calculate total percentage
        total_percentage = sum(a.get("percentage", 0) or 0 for a in self.normalized_allocations)
        
        # Get top asset classes
        top_classes = self.get_top_asset_classes(5)
        
        return {
            "total_percentage": total_percentage,
            "asset_classes": len(self.normalized_allocations),
            "top_classes": [
                {
                    "asset_class": a["asset_class"],
                    "percentage": a["percentage"]
                }
                for a in top_classes
            ]
        }

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deduplicate asset allocation entries.")
    parser.add_argument("allocations_file", help="Path to the asset allocations JSON file")
    parser.add_argument("--output-dir", help="Directory to save output files")
    
    args = parser.parse_args()
    
    # Check if the file exists
    if not os.path.exists(args.allocations_file):
        logger.error(f"Error: Allocations file not found: {args.allocations_file}")
        return 1
    
    # Read the asset allocations
    with open(args.allocations_file, "r", encoding="utf-8") as f:
        asset_allocations = json.load(f)
    
    # Deduplicate asset allocations
    deduplicator = AssetAllocationDeduplicator()
    result = deduplicator.deduplicate(asset_allocations, output_dir=args.output_dir)
    
    # Print summary
    print("\nAsset Allocation Deduplication Summary:")
    print("=====================================")
    
    print(f"Original Allocations: {len(result['original_allocations'])}")
    print(f"Deduplicated Allocations: {len(result['deduplicated_allocations'])}")
    print(f"Normalized Allocations: {len(result['normalized_allocations'])}")
    
    # Print top asset classes
    print("\nTop 5 Asset Classes by Percentage:")
    for i, allocation in enumerate(deduplicator.get_top_asset_classes(5), 1):
        print(f"{i}. {allocation['asset_class']}: {allocation['percentage']:.2f}%")
    
    # Print total percentage
    total_percentage = sum(a.get("percentage", 0) or 0 for a in result["normalized_allocations"])
    print(f"\nTotal Percentage: {total_percentage:.2f}%")
    
    return 0

if __name__ == "__main__":
    main()
