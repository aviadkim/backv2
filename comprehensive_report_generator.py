"""
Comprehensive Report Generator - Generates comprehensive reports from extraction results.

This module provides tools to generate comprehensive reports from extraction results,
including portfolio summary, asset allocation, securities, and validation results.
"""
import os
import logging
from typing import Dict, List, Any, Optional, Tuple, Set, Union
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveReportGenerator:
    """
    Generates comprehensive reports from extraction results.
    """
    
    def __init__(self):
        """Initialize the comprehensive report generator."""
        self.extraction_results = {}
        self.report_data = {}
        self.report_files = []
    
    def generate(self, extraction_results: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
        """
        Generate comprehensive reports from extraction results.
        
        Args:
            extraction_results: Dictionary containing extraction results
            output_dir: Directory to save output files
        
        Returns:
            Dict containing report generation results
        """
        logger.info("Generating comprehensive reports")
        
        # Reset data
        self.extraction_results = extraction_results
        self.report_data = {}
        self.report_files = []
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Generate portfolio summary report
            self._generate_portfolio_summary(output_dir)
            
            # Generate asset allocation report
            self._generate_asset_allocation_report(output_dir)
            
            # Generate securities report
            self._generate_securities_report(output_dir)
            
            # Generate validation report
            self._generate_validation_report(output_dir)
            
            # Generate comprehensive report
            self._generate_comprehensive_report(output_dir)
            
            logger.info("Report generation completed.")
            return {
                "report_files": self.report_files,
                "report_data": self.report_data
            }
            
        except Exception as e:
            logger.error(f"Error generating reports: {str(e)}")
            return {"error": str(e)}
    
    def _generate_portfolio_summary(self, output_dir):
        """Generate portfolio summary report."""
        # Extract portfolio value
        portfolio_value = None
        
        if "portfolio_value" in self.extraction_results:
            if isinstance(self.extraction_results["portfolio_value"], dict):
                if "value" in self.extraction_results["portfolio_value"]:
                    portfolio_value = self.extraction_results["portfolio_value"]["value"]
            elif isinstance(self.extraction_results["portfolio_value"], (int, float)):
                portfolio_value = float(self.extraction_results["portfolio_value"])
        
        if portfolio_value is None:
            logger.warning("Portfolio value not found in extraction results")
            return
        
        # Create portfolio summary data
        portfolio_summary = {
            "portfolio_value": portfolio_value,
            "extraction_date": datetime.now().strftime("%Y-%m-%d"),
            "currency": "USD"  # Assuming USD as default currency
        }
        
        # Add securities summary
        if "securities" in self.extraction_results and self.extraction_results["securities"]:
            securities = self.extraction_results["securities"]
            
            # Calculate total securities value
            securities_value = sum(security.get("valuation", 0) or 0 for security in securities)
            
            # Count securities by type
            security_types = {}
            for security in securities:
                security_type = security.get("security_type", "Unknown")
                if security_type not in security_types:
                    security_types[security_type] = 0
                security_types[security_type] += 1
            
            portfolio_summary["securities_count"] = len(securities)
            portfolio_summary["securities_value"] = securities_value
            portfolio_summary["security_types"] = security_types
            
            # Calculate coverage
            if portfolio_value > 0:
                portfolio_summary["securities_coverage"] = securities_value / portfolio_value * 100
            else:
                portfolio_summary["securities_coverage"] = 0
        
        # Add asset allocation summary
        if "asset_allocation" in self.extraction_results and self.extraction_results["asset_allocation"]:
            asset_allocation = self.extraction_results["asset_allocation"]
            
            # Filter out total rows
            non_total_allocations = [a for a in asset_allocation if not a.get("is_total", False)]
            
            # Calculate total asset allocation value
            asset_allocation_value = sum(allocation.get("value", 0) or 0 for allocation in non_total_allocations)
            
            # Calculate total percentage
            total_percentage = sum(allocation.get("percentage", 0) or 0 for allocation in non_total_allocations)
            
            portfolio_summary["asset_allocation_count"] = len(non_total_allocations)
            portfolio_summary["asset_allocation_value"] = asset_allocation_value
            portfolio_summary["asset_allocation_percentage"] = total_percentage
            
            # Calculate coverage
            if portfolio_value > 0:
                portfolio_summary["asset_allocation_coverage"] = asset_allocation_value / portfolio_value * 100
            else:
                portfolio_summary["asset_allocation_coverage"] = 0
        
        # Save portfolio summary as JSON
        summary_path = os.path.join(output_dir, "portfolio_summary.json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(portfolio_summary, f, indent=2)
        
        self.report_files.append(summary_path)
        self.report_data["portfolio_summary"] = portfolio_summary
        
        # Generate portfolio summary chart
        if "security_types" in portfolio_summary:
            chart_path = os.path.join(output_dir, "portfolio_summary_chart.png")
            
            # Create pie chart
            plt.figure(figsize=(10, 6))
            plt.pie(
                portfolio_summary["security_types"].values(),
                labels=portfolio_summary["security_types"].keys(),
                autopct='%1.1f%%',
                startangle=90
            )
            plt.axis('equal')
            plt.title('Securities by Type')
            plt.savefig(chart_path)
            plt.close()
            
            self.report_files.append(chart_path)
        
        logger.info(f"Generated portfolio summary report: {summary_path}")
    
    def _generate_asset_allocation_report(self, output_dir):
        """Generate asset allocation report."""
        if "asset_allocation" not in self.extraction_results or not self.extraction_results["asset_allocation"]:
            logger.warning("Asset allocation not found in extraction results")
            return
        
        asset_allocation = self.extraction_results["asset_allocation"]
        
        # Filter out total rows
        non_total_allocations = [a for a in asset_allocation if not a.get("is_total", False)]
        
        # Create asset allocation data
        asset_allocation_data = {
            "allocations": non_total_allocations,
            "total_count": len(non_total_allocations),
            "extraction_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Calculate total value and percentage
        total_value = sum(allocation.get("value", 0) or 0 for allocation in non_total_allocations)
        total_percentage = sum(allocation.get("percentage", 0) or 0 for allocation in non_total_allocations)
        
        asset_allocation_data["total_value"] = total_value
        asset_allocation_data["total_percentage"] = total_percentage
        
        # Normalize percentages if total is not close to 100%
        if abs(total_percentage - 100) > 5:
            normalized_allocations = []
            
            for allocation in non_total_allocations:
                normalized = dict(allocation)
                
                if "percentage" in normalized and normalized["percentage"] is not None:
                    normalized["original_percentage"] = normalized["percentage"]
                    normalized["percentage"] = (normalized["percentage"] / total_percentage) * 100
                
                normalized_allocations.append(normalized)
            
            asset_allocation_data["normalized_allocations"] = normalized_allocations
        
        # Save asset allocation as JSON
        allocation_path = os.path.join(output_dir, "asset_allocation.json")
        with open(allocation_path, "w", encoding="utf-8") as f:
            json.dump(asset_allocation_data, f, indent=2)
        
        self.report_files.append(allocation_path)
        self.report_data["asset_allocation"] = asset_allocation_data
        
        # Generate asset allocation chart
        chart_path = os.path.join(output_dir, "asset_allocation_chart.png")
        
        # Create pie chart
        plt.figure(figsize=(10, 6))
        
        # Use normalized allocations if available
        if "normalized_allocations" in asset_allocation_data:
            allocations = asset_allocation_data["normalized_allocations"]
        else:
            allocations = non_total_allocations
        
        # Filter allocations with percentage
        allocations_with_percentage = [a for a in allocations if a.get("percentage")]
        
        # Sort by percentage (descending)
        sorted_allocations = sorted(allocations_with_percentage, key=lambda a: a["percentage"], reverse=True)
        
        # Limit to top 10 allocations for readability
        top_allocations = sorted_allocations[:10]
        
        # Create pie chart
        plt.pie(
            [a["percentage"] for a in top_allocations],
            labels=[a["asset_class"] for a in top_allocations],
            autopct='%1.1f%%',
            startangle=90
        )
        plt.axis('equal')
        plt.title('Asset Allocation')
        plt.savefig(chart_path)
        plt.close()
        
        self.report_files.append(chart_path)
        
        # Create asset allocation table as CSV
        csv_path = os.path.join(output_dir, "asset_allocation.csv")
        
        # Create DataFrame
        df = pd.DataFrame(sorted_allocations)
        
        # Select relevant columns
        if "normalized_allocations" in asset_allocation_data:
            columns = ["asset_class", "value", "original_percentage", "percentage"]
        else:
            columns = ["asset_class", "value", "percentage"]
        
        # Filter columns that exist in the DataFrame
        existing_columns = [col for col in columns if col in df.columns]
        
        # Save as CSV
        df[existing_columns].to_csv(csv_path, index=False)
        
        self.report_files.append(csv_path)
        
        logger.info(f"Generated asset allocation report: {allocation_path}")
    
    def _generate_securities_report(self, output_dir):
        """Generate securities report."""
        if "securities" not in self.extraction_results or not self.extraction_results["securities"]:
            logger.warning("Securities not found in extraction results")
            return
        
        securities = self.extraction_results["securities"]
        
        # Create securities data
        securities_data = {
            "securities": securities,
            "total_count": len(securities),
            "extraction_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Calculate total value
        total_value = sum(security.get("valuation", 0) or 0 for security in securities)
        securities_data["total_value"] = total_value
        
        # Group securities by type
        securities_by_type = defaultdict(list)
        for security in securities:
            security_type = security.get("security_type", "Unknown")
            securities_by_type[security_type].append(security)
        
        securities_data["securities_by_type"] = {
            security_type: {
                "count": len(securities_list),
                "value": sum(security.get("valuation", 0) or 0 for security in securities_list)
            }
            for security_type, securities_list in securities_by_type.items()
        }
        
        # Get top securities by valuation
        securities_with_valuation = [s for s in securities if s.get("valuation")]
        sorted_securities = sorted(securities_with_valuation, key=lambda s: s["valuation"], reverse=True)
        top_securities = sorted_securities[:10]
        
        securities_data["top_securities"] = top_securities
        
        # Save securities as JSON
        securities_path = os.path.join(output_dir, "securities.json")
        with open(securities_path, "w", encoding="utf-8") as f:
            json.dump(securities_data, f, indent=2)
        
        self.report_files.append(securities_path)
        self.report_data["securities"] = securities_data
        
        # Generate securities chart
        chart_path = os.path.join(output_dir, "securities_by_type_chart.png")
        
        # Create pie chart
        plt.figure(figsize=(10, 6))
        plt.pie(
            [data["value"] for data in securities_data["securities_by_type"].values()],
            labels=securities_data["securities_by_type"].keys(),
            autopct='%1.1f%%',
            startangle=90
        )
        plt.axis('equal')
        plt.title('Securities by Type')
        plt.savefig(chart_path)
        plt.close()
        
        self.report_files.append(chart_path)
        
        # Create top securities chart
        top_chart_path = os.path.join(output_dir, "top_securities_chart.png")
        
        # Create bar chart
        plt.figure(figsize=(12, 8))
        plt.barh(
            [f"{s.get('description', s.get('isin', 'Unknown'))[:30]}" for s in top_securities],
            [s["valuation"] for s in top_securities]
        )
        plt.xlabel('Valuation')
        plt.ylabel('Security')
        plt.title('Top 10 Securities by Valuation')
        plt.tight_layout()
        plt.savefig(top_chart_path)
        plt.close()
        
        self.report_files.append(top_chart_path)
        
        # Create securities table as CSV
        csv_path = os.path.join(output_dir, "securities.csv")
        
        # Create DataFrame
        df = pd.DataFrame(securities)
        
        # Select relevant columns
        columns = ["isin", "description", "security_type", "valuation"]
        
        # Filter columns that exist in the DataFrame
        existing_columns = [col for col in columns if col in df.columns]
        
        # Save as CSV
        df[existing_columns].to_csv(csv_path, index=False)
        
        self.report_files.append(csv_path)
        
        logger.info(f"Generated securities report: {securities_path}")
    
    def _generate_validation_report(self, output_dir):
        """Generate validation report."""
        if "validation" not in self.extraction_results:
            logger.warning("Validation results not found in extraction results")
            return
        
        validation = self.extraction_results["validation"]
        
        # Save validation as JSON
        validation_path = os.path.join(output_dir, "validation.json")
        with open(validation_path, "w", encoding="utf-8") as f:
            json.dump(validation, f, indent=2)
        
        self.report_files.append(validation_path)
        self.report_data["validation"] = validation
        
        # Create validation summary as text
        summary_path = os.path.join(output_dir, "validation_summary.txt")
        
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write("Validation Summary\n")
            f.write("=================\n\n")
            
            for section, result in validation.items():
                f.write(f"{section.capitalize()}: {'Valid' if result.get('valid', False) else 'Invalid'}\n")
                
                if "issues" in result and result["issues"]:
                    f.write(f"  Issues ({len(result['issues'])}):\n")
                    for issue in result["issues"]:
                        f.write(f"  - {issue}\n")
                
                f.write("\n")
        
        self.report_files.append(summary_path)
        
        logger.info(f"Generated validation report: {validation_path}")
    
    def _generate_comprehensive_report(self, output_dir):
        """Generate comprehensive report."""
        # Create comprehensive report as HTML
        html_path = os.path.join(output_dir, "comprehensive_report.html")
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write("<!DOCTYPE html>\n")
            f.write("<html>\n")
            f.write("<head>\n")
            f.write("  <title>Comprehensive Financial Report</title>\n")
            f.write("  <style>\n")
            f.write("    body { font-family: Arial, sans-serif; margin: 20px; }\n")
            f.write("    h1 { color: #2c3e50; }\n")
            f.write("    h2 { color: #3498db; }\n")
            f.write("    table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }\n")
            f.write("    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }\n")
            f.write("    th { background-color: #f2f2f2; }\n")
            f.write("    tr:nth-child(even) { background-color: #f9f9f9; }\n")
            f.write("    .section { margin-bottom: 30px; }\n")
            f.write("    .chart { margin: 20px 0; max-width: 100%; height: auto; }\n")
            f.write("    .valid { color: green; }\n")
            f.write("    .invalid { color: red; }\n")
            f.write("  </style>\n")
            f.write("</head>\n")
            f.write("<body>\n")
            
            # Header
            f.write("  <h1>Comprehensive Financial Report</h1>\n")
            f.write(f"  <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>\n")
            
            # Portfolio Summary
            f.write("  <div class='section'>\n")
            f.write("    <h2>Portfolio Summary</h2>\n")
            
            if "portfolio_summary" in self.report_data:
                portfolio_summary = self.report_data["portfolio_summary"]
                
                f.write("    <table>\n")
                f.write("      <tr><th>Metric</th><th>Value</th></tr>\n")
                f.write(f"      <tr><td>Portfolio Value</td><td>${portfolio_summary['portfolio_value']:,.2f}</td></tr>\n")
                f.write(f"      <tr><td>Currency</td><td>{portfolio_summary.get('currency', 'USD')}</td></tr>\n")
                f.write(f"      <tr><td>Extraction Date</td><td>{portfolio_summary.get('extraction_date', '')}</td></tr>\n")
                
                if "securities_count" in portfolio_summary:
                    f.write(f"      <tr><td>Securities Count</td><td>{portfolio_summary['securities_count']}</td></tr>\n")
                
                if "securities_value" in portfolio_summary:
                    f.write(f"      <tr><td>Securities Value</td><td>${portfolio_summary['securities_value']:,.2f}</td></tr>\n")
                
                if "securities_coverage" in portfolio_summary:
                    f.write(f"      <tr><td>Securities Coverage</td><td>{portfolio_summary['securities_coverage']:.2f}%</td></tr>\n")
                
                if "asset_allocation_count" in portfolio_summary:
                    f.write(f"      <tr><td>Asset Allocation Count</td><td>{portfolio_summary['asset_allocation_count']}</td></tr>\n")
                
                if "asset_allocation_value" in portfolio_summary:
                    f.write(f"      <tr><td>Asset Allocation Value</td><td>${portfolio_summary['asset_allocation_value']:,.2f}</td></tr>\n")
                
                if "asset_allocation_coverage" in portfolio_summary:
                    f.write(f"      <tr><td>Asset Allocation Coverage</td><td>{portfolio_summary['asset_allocation_coverage']:.2f}%</td></tr>\n")
                
                f.write("    </table>\n")
                
                # Add chart if available
                chart_path = os.path.join(output_dir, "portfolio_summary_chart.png")
                if os.path.exists(chart_path):
                    f.write(f"    <img class='chart' src='portfolio_summary_chart.png' alt='Portfolio Summary Chart'>\n")
            else:
                f.write("    <p>No portfolio summary data available.</p>\n")
            
            f.write("  </div>\n")
            
            # Asset Allocation
            f.write("  <div class='section'>\n")
            f.write("    <h2>Asset Allocation</h2>\n")
            
            if "asset_allocation" in self.report_data:
                asset_allocation = self.report_data["asset_allocation"]
                
                f.write("    <table>\n")
                f.write("      <tr><th>Metric</th><th>Value</th></tr>\n")
                f.write(f"      <tr><td>Total Count</td><td>{asset_allocation['total_count']}</td></tr>\n")
                f.write(f"      <tr><td>Total Value</td><td>${asset_allocation['total_value']:,.2f}</td></tr>\n")
                f.write(f"      <tr><td>Total Percentage</td><td>{asset_allocation['total_percentage']:.2f}%</td></tr>\n")
                f.write("    </table>\n")
                
                # Add top allocations table
                if "normalized_allocations" in asset_allocation:
                    allocations = asset_allocation["normalized_allocations"]
                else:
                    allocations = asset_allocation["allocations"]
                
                # Filter allocations with percentage
                allocations_with_percentage = [a for a in allocations if a.get("percentage")]
                
                # Sort by percentage (descending)
                sorted_allocations = sorted(allocations_with_percentage, key=lambda a: a["percentage"], reverse=True)
                
                # Limit to top 10 allocations for readability
                top_allocations = sorted_allocations[:10]
                
                if top_allocations:
                    f.write("    <h3>Top Asset Classes</h3>\n")
                    f.write("    <table>\n")
                    f.write("      <tr><th>Asset Class</th><th>Value</th><th>Percentage</th></tr>\n")
                    
                    for allocation in top_allocations:
                        f.write(f"      <tr><td>{allocation['asset_class']}</td><td>${allocation.get('value', 0):,.2f}</td><td>{allocation['percentage']:.2f}%</td></tr>\n")
                    
                    f.write("    </table>\n")
                
                # Add chart if available
                chart_path = os.path.join(output_dir, "asset_allocation_chart.png")
                if os.path.exists(chart_path):
                    f.write(f"    <img class='chart' src='asset_allocation_chart.png' alt='Asset Allocation Chart'>\n")
            else:
                f.write("    <p>No asset allocation data available.</p>\n")
            
            f.write("  </div>\n")
            
            # Securities
            f.write("  <div class='section'>\n")
            f.write("    <h2>Securities</h2>\n")
            
            if "securities" in self.report_data:
                securities_data = self.report_data["securities"]
                
                f.write("    <table>\n")
                f.write("      <tr><th>Metric</th><th>Value</th></tr>\n")
                f.write(f"      <tr><td>Total Count</td><td>{securities_data['total_count']}</td></tr>\n")
                f.write(f"      <tr><td>Total Value</td><td>${securities_data['total_value']:,.2f}</td></tr>\n")
                f.write("    </table>\n")
                
                # Add securities by type table
                if "securities_by_type" in securities_data:
                    f.write("    <h3>Securities by Type</h3>\n")
                    f.write("    <table>\n")
                    f.write("      <tr><th>Security Type</th><th>Count</th><th>Value</th></tr>\n")
                    
                    for security_type, data in securities_data["securities_by_type"].items():
                        f.write(f"      <tr><td>{security_type}</td><td>{data['count']}</td><td>${data['value']:,.2f}</td></tr>\n")
                    
                    f.write("    </table>\n")
                
                # Add top securities table
                if "top_securities" in securities_data:
                    f.write("    <h3>Top Securities by Valuation</h3>\n")
                    f.write("    <table>\n")
                    f.write("      <tr><th>ISIN</th><th>Description</th><th>Type</th><th>Valuation</th></tr>\n")
                    
                    for security in securities_data["top_securities"]:
                        f.write(f"      <tr><td>{security.get('isin', '')}</td><td>{security.get('description', '')}</td><td>{security.get('security_type', '')}</td><td>${security.get('valuation', 0):,.2f}</td></tr>\n")
                    
                    f.write("    </table>\n")
                
                # Add charts if available
                chart_path = os.path.join(output_dir, "securities_by_type_chart.png")
                if os.path.exists(chart_path):
                    f.write(f"    <img class='chart' src='securities_by_type_chart.png' alt='Securities by Type Chart'>\n")
                
                top_chart_path = os.path.join(output_dir, "top_securities_chart.png")
                if os.path.exists(top_chart_path):
                    f.write(f"    <img class='chart' src='top_securities_chart.png' alt='Top Securities Chart'>\n")
            else:
                f.write("    <p>No securities data available.</p>\n")
            
            f.write("  </div>\n")
            
            # Validation
            f.write("  <div class='section'>\n")
            f.write("    <h2>Validation</h2>\n")
            
            if "validation" in self.report_data:
                validation = self.report_data["validation"]
                
                f.write("    <table>\n")
                f.write("      <tr><th>Section</th><th>Status</th><th>Issues</th></tr>\n")
                
                for section, result in validation.items():
                    is_valid = result.get("valid", False)
                    issues = result.get("issues", [])
                    
                    f.write(f"      <tr><td>{section.capitalize()}</td><td class=\"{'valid' if is_valid else 'invalid'}\">{('Valid' if is_valid else 'Invalid')}</td><td>{len(issues)}</td></tr>\n")
                
                f.write("    </table>\n")
                
                # Add issues table
                all_issues = []
                for section, result in validation.items():
                    for issue in result.get("issues", []):
                        all_issues.append({
                            "section": section,
                            "issue": issue
                        })
                
                if all_issues:
                    f.write("    <h3>Validation Issues</h3>\n")
                    f.write("    <table>\n")
                    f.write("      <tr><th>Section</th><th>Issue</th></tr>\n")
                    
                    for issue_data in all_issues:
                        f.write(f"      <tr><td>{issue_data['section'].capitalize()}</td><td>{issue_data['issue']}</td></tr>\n")
                    
                    f.write("    </table>\n")
            else:
                f.write("    <p>No validation data available.</p>\n")
            
            f.write("  </div>\n")
            
            f.write("</body>\n")
            f.write("</html>\n")
        
        self.report_files.append(html_path)
        
        logger.info(f"Generated comprehensive report: {html_path}")
    
    def get_report_files(self) -> List[str]:
        """
        Get the list of generated report files.
        
        Returns:
            List of report file paths
        """
        return self.report_files
    
    def get_report_data(self) -> Dict[str, Any]:
        """
        Get the report data.
        
        Returns:
            Dict containing report data
        """
        return self.report_data

def main():
    """Main function."""
    import argparse
    from collections import defaultdict
    
    parser = argparse.ArgumentParser(description="Generate comprehensive reports from extraction results.")
    parser.add_argument("extraction_file", help="Path to the extraction results JSON file")
    parser.add_argument("--output-dir", required=True, help="Directory to save output files")
    
    args = parser.parse_args()
    
    # Check if the file exists
    if not os.path.exists(args.extraction_file):
        logger.error(f"Error: Extraction file not found: {args.extraction_file}")
        return 1
    
    # Read the extraction results
    with open(args.extraction_file, "r", encoding="utf-8") as f:
        extraction_results = json.load(f)
    
    # Generate reports
    generator = ComprehensiveReportGenerator()
    result = generator.generate(extraction_results, args.output_dir)
    
    # Print summary
    print("\nReport Generation Summary:")
    print("========================")
    
    print(f"Generated {len(result['report_files'])} report files:")
    for file_path in result['report_files']:
        print(f"- {file_path}")
    
    return 0

if __name__ == "__main__":
    main()
