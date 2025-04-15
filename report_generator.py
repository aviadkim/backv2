"""
Report Generator - Generates reports from financial document comparison data.
"""
import os
import csv
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("ReportLab not available. Install with: pip install reportlab")

class ReportGenerator:
    """
    Generates reports from financial document comparison data.
    """

    def __init__(self):
        """Initialize the report generator."""
        pass

    def generate_html_report(self, comparison_data: Dict[str, Any], output_path: str) -> str:
        """
        Generate an HTML report from comparison data.

        Args:
            comparison_data: Comparison data from MultiDocumentProcessor
            output_path: Path to save the HTML report

        Returns:
            Path to the generated HTML report
        """
        # Create HTML content
        html_content = self._create_html_content(comparison_data)

        # Save HTML file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"HTML report saved to: {output_path}")
        return output_path

    def _create_html_content(self, comparison_data: Dict[str, Any]) -> str:
        """
        Create HTML content from comparison data.

        Args:
            comparison_data: Comparison data from MultiDocumentProcessor

        Returns:
            HTML content as string
        """
        # Extract basic information
        doc1_id = comparison_data.get("doc1_id", "Unknown")
        doc2_id = comparison_data.get("doc2_id", "Unknown")
        doc1_date = comparison_data.get("doc1_date", "Unknown")
        doc2_date = comparison_data.get("doc2_date", "Unknown")
        chronological_order = comparison_data.get("chronological_order", "unknown")
        time_between = comparison_data.get("time_between_documents", {})

        # Portfolio summary
        portfolio = comparison_data.get("portfolio_summary", {})

        # Performance metrics
        metrics = comparison_data.get("performance_metrics", {})

        # Asset allocation changes
        asset_allocation = comparison_data.get("asset_allocation_changes", {})

        # Securities
        security_changes = comparison_data.get("security_changes", [])
        new_securities = comparison_data.get("new_securities", [])
        removed_securities = comparison_data.get("removed_securities", [])
        top_gainers = comparison_data.get("top_gainers", [])
        top_losers = comparison_data.get("top_losers", [])

        # Create HTML content
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Financial Document Comparison Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        h1 {{
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 5px;
            margin-top: 30px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .positive {{
            color: green;
        }}
        .negative {{
            color: red;
        }}
        .summary-box {{
            background-color: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
        }}
        .summary-item {{
            margin: 10px 0;
        }}
        .summary-label {{
            font-weight: bold;
            display: inline-block;
            width: 200px;
        }}
        .chart-container {{
            width: 100%;
            height: 400px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <h1>Financial Document Comparison Report</h1>

    <div class="summary-box">
        <h2>Document Information</h2>
        <div class="summary-item">
            <span class="summary-label">Document 1:</span>
            <span>{doc1_id} ({doc1_date})</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">Document 2:</span>
            <span>{doc2_id} ({doc2_date})</span>
        </div>

        {self._format_time_between_html(time_between)}

        {self._format_chronological_order_html(chronological_order)}

        <div class="summary-item">
            <span class="summary-label">Report Generated:</span>
            <span>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</span>
        </div>
    </div>

    <h2>Portfolio Summary</h2>
    {self._format_portfolio_summary_html(portfolio)}

    <h2>Performance Metrics</h2>
    {self._format_performance_metrics_html(metrics)}

    <h2>Asset Allocation Changes</h2>
    {self._format_asset_allocation_html(asset_allocation)}

    <h2>Security Changes</h2>

    <h3>Top Gainers</h3>
    {self._format_securities_table_html(top_gainers, limit=10)}

    <h3>Top Losers</h3>
    {self._format_securities_table_html(top_losers, limit=10)}

    <h3>New Securities</h3>
    {self._format_securities_table_html(new_securities, limit=10, new_securities=True)}

    <h3>Removed Securities</h3>
    {self._format_securities_table_html(removed_securities, limit=10, removed_securities=True)}

    <h3>All Security Changes</h3>
    {self._format_securities_table_html(security_changes, limit=50)}

    <div style="margin-top: 50px; text-align: center; color: #7f8c8d; font-size: 0.8em;">
        <p>Generated by Financial Document Analyzer</p>
    </div>
</body>
</html>
"""
        return html

    def _format_time_between_html(self, time_between: Dict[str, Any]) -> str:
        """Format time between documents as HTML."""
        if not time_between:
            return ""

        days = time_between.get("days")
        months = time_between.get("months")
        years = time_between.get("years")

        if days is None:
            return ""

        return f"""
        <div class="summary-item">
            <span class="summary-label">Time Between Documents:</span>
            <span>{days} days ({months} months, {years:.2f} years)</span>
        </div>
        """

    def _format_chronological_order_html(self, order: str) -> str:
        """Format chronological order as HTML."""
        if not order or order == "unknown":
            return ""

        order_text = ""
        if order == "chronological":
            order_text = "Documents are in chronological order (Document 1 is older)"
        elif order == "reverse_chronological":
            order_text = "Documents are in reverse chronological order (Document 2 is older)"
        elif order == "same_date":
            order_text = "Documents have the same date"

        return f"""
        <div class="summary-item">
            <span class="summary-label">Chronological Order:</span>
            <span>{order_text}</span>
        </div>
        """

    def _format_portfolio_summary_html(self, portfolio: Dict[str, Any]) -> str:
        """Format portfolio summary as HTML."""
        if not portfolio:
            return "<p>No portfolio summary available.</p>"

        value1 = portfolio.get("value1")
        value2 = portfolio.get("value2")
        absolute_change = portfolio.get("absolute_change")
        percentage_change = portfolio.get("percentage_change")
        annualized_return = portfolio.get("annualized_return")

        if value1 is None or value2 is None:
            return "<p>Insufficient portfolio data available.</p>"

        change_class = "positive" if absolute_change and absolute_change > 0 else "negative"

        html = f"""
        <div class="summary-box">
            <div class="summary-item">
                <span class="summary-label">Document 1 Value:</span>
                <span>${value1:,.2f}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Document 2 Value:</span>
                <span>${value2:,.2f}</span>
            </div>
        """

        if absolute_change is not None:
            html += f"""
            <div class="summary-item">
                <span class="summary-label">Absolute Change:</span>
                <span class="{change_class}">${absolute_change:,.2f}</span>
            </div>
            """

        if percentage_change is not None:
            html += f"""
            <div class="summary-item">
                <span class="summary-label">Percentage Change:</span>
                <span class="{change_class}">{percentage_change:.2f}%</span>
            </div>
            """

        if annualized_return is not None:
            ann_return_class = "positive" if annualized_return > 0 else "negative"
            html += f"""
            <div class="summary-item">
                <span class="summary-label">Annualized Return:</span>
                <span class="{ann_return_class}">{annualized_return:.2f}%</span>
            </div>
            """

        html += "</div>"
        return html

    def _format_performance_metrics_html(self, metrics: Dict[str, Any]) -> str:
        """Format performance metrics as HTML."""
        if not metrics:
            return "<p>No performance metrics available.</p>"

        total_return = metrics.get("total_return")
        annualized_return = metrics.get("annualized_return")
        volatility = metrics.get("volatility")
        sharpe_ratio = metrics.get("sharpe_ratio")

        if total_return is None and annualized_return is None:
            return "<p>Insufficient performance data available.</p>"

        html = "<div class=\"summary-box\">"

        if total_return is not None:
            total_return_class = "positive" if total_return > 0 else "negative"
            html += f"""
            <div class="summary-item">
                <span class="summary-label">Total Return:</span>
                <span class="{total_return_class}">{total_return:.2f}%</span>
            </div>
            """

        if annualized_return is not None:
            ann_return_class = "positive" if annualized_return > 0 else "negative"
            html += f"""
            <div class="summary-item">
                <span class="summary-label">Annualized Return:</span>
                <span class="{ann_return_class}">{annualized_return:.2f}%</span>
            </div>
            """

        if volatility is not None:
            html += f"""
            <div class="summary-item">
                <span class="summary-label">Volatility:</span>
                <span>{volatility:.2f}%</span>
            </div>
            """

        if sharpe_ratio is not None:
            sharpe_class = "positive" if sharpe_ratio > 1 else ""
            html += f"""
            <div class="summary-item">
                <span class="summary-label">Sharpe Ratio:</span>
                <span class="{sharpe_class}">{sharpe_ratio:.2f}</span>
            </div>
            """

        # Asset class contribution
        contributions = metrics.get("asset_class_contribution", {})
        if contributions:
            html += """
            <h3>Asset Class Contribution to Return</h3>
            <table>
                <tr>
                    <th>Asset Class</th>
                    <th>Weight</th>
                    <th>Return</th>
                    <th>Contribution</th>
                </tr>
            """

            for asset_class, data in contributions.items():
                weight = data.get("weight", 0)
                asset_return = data.get("return", 0)
                contribution = data.get("contribution", 0)

                return_class = "positive" if asset_return > 0 else "negative"
                contrib_class = "positive" if contribution > 0 else "negative"

                html += f"""
                <tr>
                    <td>{asset_class}</td>
                    <td>{weight:.2f}%</td>
                    <td class="{return_class}">{asset_return:.2f}%</td>
                    <td class="{contrib_class}">{contribution:.2f}%</td>
                </tr>
                """

            html += "</table>"

        html += "</div>"
        return html

    def _format_asset_allocation_html(self, asset_allocation: Dict[str, Any]) -> str:
        """Format asset allocation as HTML."""
        if not asset_allocation:
            return "<p>No asset allocation data available.</p>"

        html = """
        <table>
            <tr>
                <th>Asset Class</th>
                <th>Document 1 Value</th>
                <th>Document 2 Value</th>
                <th>Value Change</th>
                <th>Document 1 %</th>
                <th>Document 2 %</th>
                <th>% Point Change</th>
            </tr>
        """

        for asset_class, data in asset_allocation.items():
            value1 = data.get("value1", 0)
            value2 = data.get("value2", 0)
            value_change = data.get("value_change", 0)
            percentage1 = data.get("percentage1", 0)
            percentage2 = data.get("percentage2", 0)
            percentage_point_change = data.get("percentage_point_change", 0)

            value_change_class = "positive" if value_change > 0 else "negative"
            pp_change_class = "positive" if percentage_point_change > 0 else "negative"

            html += f"""
            <tr>
                <td><strong>{asset_class}</strong></td>
                <td>${value1:,.2f}</td>
                <td>${value2:,.2f}</td>
                <td class="{value_change_class}">${value_change:,.2f}</td>
                <td>{percentage1:.2f}%</td>
                <td>{percentage2:.2f}%</td>
                <td class="{pp_change_class}">{percentage_point_change:.2f}%</td>
            </tr>
            """

            # Add sub-classes if available
            sub_classes = data.get("sub_classes", {})
            for sub_class, sub_data in sub_classes.items():
                sub_value1 = sub_data.get("value1", 0)
                sub_value2 = sub_data.get("value2", 0)
                sub_value_change = sub_data.get("value_change", 0)
                sub_percentage1 = sub_data.get("percentage1", 0)
                sub_percentage2 = sub_data.get("percentage2", 0)
                sub_pp_change = sub_data.get("percentage_point_change", 0)

                sub_value_change_class = "positive" if sub_value_change > 0 else "negative"
                sub_pp_change_class = "positive" if sub_pp_change > 0 else "negative"

                html += f"""
                <tr>
                    <td style="padding-left: 30px;">{sub_class}</td>
                    <td>${sub_value1:,.2f}</td>
                    <td>${sub_value2:,.2f}</td>
                    <td class="{sub_value_change_class}">${sub_value_change:,.2f}</td>
                    <td>{sub_percentage1:.2f}%</td>
                    <td>{sub_percentage2:.2f}%</td>
                    <td class="{sub_pp_change_class}">{sub_pp_change:.2f}%</td>
                </tr>
                """

        html += "</table>"
        return html

    def _format_securities_table_html(self, securities: List[Dict[str, Any]], limit: int = 10,
                                     new_securities: bool = False, removed_securities: bool = False) -> str:
        """Format securities as HTML table."""
        if not securities:
            return "<p>No securities data available.</p>"

        # Limit the number of securities to display
        securities = securities[:limit]

        if new_securities:
            html = """
            <table>
                <tr>
                    <th>Security</th>
                    <th>ISIN</th>
                    <th>Valuation</th>
                </tr>
            """

            for security in securities:
                description = security.get("description", "Unknown")
                isin = security.get("isin", "N/A")
                valuation = security.get("valuation2", 0)

                html += f"""
                <tr>
                    <td>{description}</td>
                    <td>{isin}</td>
                    <td>${valuation:,.2f}</td>
                </tr>
                """

        elif removed_securities:
            html = """
            <table>
                <tr>
                    <th>Security</th>
                    <th>ISIN</th>
                    <th>Valuation</th>
                </tr>
            """

            for security in securities:
                description = security.get("description", "Unknown")
                isin = security.get("isin", "N/A")
                valuation = security.get("valuation1", 0)

                html += f"""
                <tr>
                    <td>{description}</td>
                    <td>{isin}</td>
                    <td>${valuation:,.2f}</td>
                </tr>
                """

        else:
            html = """
            <table>
                <tr>
                    <th>Security</th>
                    <th>ISIN</th>
                    <th>Document 1 Value</th>
                    <th>Document 2 Value</th>
                    <th>Value Change</th>
                    <th>% Change</th>
                </tr>
            """

            for security in securities:
                description = security.get("description", "Unknown")
                isin = security.get("isin", "N/A")
                valuation1 = security.get("valuation1", 0)
                valuation2 = security.get("valuation2", 0)
                valuation_change = security.get("valuation_change", 0)
                percentage_change = security.get("percentage_change", 0)

                in_doc1 = security.get("in_doc1", False)
                in_doc2 = security.get("in_doc2", False)

                value_change_class = "positive" if valuation_change > 0 else "negative"
                percentage_change_class = "positive" if percentage_change and percentage_change > 0 else "negative"

                if in_doc1 and in_doc2:
                    val1_str = f"${valuation1:,.2f}" if valuation1 is not None else "N/A"
                    val2_str = f"${valuation2:,.2f}" if valuation2 is not None else "N/A"
                    val_change_str = f"${valuation_change:,.2f}" if valuation_change is not None else "N/A"
                    pct_change_str = f"{percentage_change:.2f}%" if percentage_change is not None else "N/A"

                    html += f"""
                    <tr>
                        <td>{description}</td>
                        <td>{isin}</td>
                        <td>{val1_str}</td>
                        <td>{val2_str}</td>
                        <td class="{value_change_class}">{val_change_str}</td>
                        <td class="{percentage_change_class}">{pct_change_str}</td>
                    </tr>
                    """
                elif in_doc1:
                    val1_str = f"${valuation1:,.2f}" if valuation1 is not None else "N/A"
                    val_change_str = f"-${valuation1:,.2f}" if valuation1 is not None else "N/A"

                    html += f"""
                    <tr>
                        <td>{description}</td>
                        <td>{isin}</td>
                        <td>{val1_str}</td>
                        <td>N/A</td>
                        <td class="negative">{val_change_str}</td>
                        <td class="negative">-100.00%</td>
                    </tr>
                    """
                elif in_doc2:
                    val2_str = f"${valuation2:,.2f}" if valuation2 is not None else "N/A"
                    val_change_str = f"${valuation2:,.2f}" if valuation2 is not None else "N/A"

                    html += f"""
                    <tr>
                        <td>{description}</td>
                        <td>{isin}</td>
                        <td>N/A</td>
                        <td>{val2_str}</td>
                        <td class="positive">{val_change_str}</td>
                        <td class="positive">N/A</td>
                    </tr>
                    """

        html += "</table>"
        return html

    def export_to_csv(self, comparison_data: Dict[str, Any], output_dir: str) -> List[str]:
        """
        Export comparison data to CSV files.

        Args:
            comparison_data: Comparison data from MultiDocumentProcessor
            output_dir: Directory to save CSV files

        Returns:
            List of paths to the generated CSV files
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Generate CSV files
        csv_files = []

        # Portfolio summary
        portfolio_path = os.path.join(output_dir, "portfolio_summary.csv")
        self._export_portfolio_summary_csv(comparison_data, portfolio_path)
        csv_files.append(portfolio_path)

        # Asset allocation
        asset_allocation_path = os.path.join(output_dir, "asset_allocation.csv")
        self._export_asset_allocation_csv(comparison_data, asset_allocation_path)
        csv_files.append(asset_allocation_path)

        # Securities
        securities_path = os.path.join(output_dir, "securities.csv")
        self._export_securities_csv(comparison_data, securities_path)
        csv_files.append(securities_path)

        print(f"CSV files exported to: {output_dir}")
        return csv_files

    def _export_portfolio_summary_csv(self, comparison_data: Dict[str, Any], output_path: str):
        """Export portfolio summary to CSV."""
        portfolio = comparison_data.get("portfolio_summary", {})
        metrics = comparison_data.get("performance_metrics", {})

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow(["Metric", "Value"])

            # Write portfolio summary
            writer.writerow(["Document 1 Value", portfolio.get("value1", "")])
            writer.writerow(["Document 2 Value", portfolio.get("value2", "")])
            writer.writerow(["Absolute Change", portfolio.get("absolute_change", "")])
            writer.writerow(["Percentage Change", portfolio.get("percentage_change", "")])
            writer.writerow(["Annualized Return", portfolio.get("annualized_return", "")])

            # Write performance metrics
            writer.writerow([])
            writer.writerow(["Performance Metrics", ""])
            writer.writerow(["Total Return", metrics.get("total_return", "")])
            writer.writerow(["Annualized Return", metrics.get("annualized_return", "")])
            writer.writerow(["Volatility", metrics.get("volatility", "")])
            writer.writerow(["Sharpe Ratio", metrics.get("sharpe_ratio", "")])

    def _export_asset_allocation_csv(self, comparison_data: Dict[str, Any], output_path: str):
        """Export asset allocation to CSV."""
        asset_allocation = comparison_data.get("asset_allocation_changes", {})

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow([
                "Asset Class", "Document 1 Value", "Document 2 Value", "Value Change",
                "Document 1 %", "Document 2 %", "% Point Change"
            ])

            # Write asset allocation data
            for asset_class, data in asset_allocation.items():
                writer.writerow([
                    asset_class,
                    data.get("value1", ""),
                    data.get("value2", ""),
                    data.get("value_change", ""),
                    data.get("percentage1", ""),
                    data.get("percentage2", ""),
                    data.get("percentage_point_change", "")
                ])

                # Write sub-classes
                sub_classes = data.get("sub_classes", {})
                for sub_class, sub_data in sub_classes.items():
                    writer.writerow([
                        f"  {sub_class}",
                        sub_data.get("value1", ""),
                        sub_data.get("value2", ""),
                        sub_data.get("value_change", ""),
                        sub_data.get("percentage1", ""),
                        sub_data.get("percentage2", ""),
                        sub_data.get("percentage_point_change", "")
                    ])

    def _export_securities_csv(self, comparison_data: Dict[str, Any], output_path: str):
        """Export securities to CSV."""
        securities = comparison_data.get("security_changes", [])

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow([
                "Security", "ISIN", "In Doc 1", "In Doc 2", "Document 1 Value",
                "Document 2 Value", "Value Change", "% Change"
            ])

            # Write securities data
            for security in securities:
                writer.writerow([
                    security.get("description", ""),
                    security.get("isin", ""),
                    security.get("in_doc1", ""),
                    security.get("in_doc2", ""),
                    security.get("valuation1", ""),
                    security.get("valuation2", ""),
                    security.get("valuation_change", ""),
                    security.get("percentage_change", "")
                ])

    def generate_pdf_report(self, comparison_data: Dict[str, Any], output_path: str) -> str:
        """
        Generate a PDF report from comparison data.

        Args:
            comparison_data: Comparison data from MultiDocumentProcessor
            output_path: Path to save the PDF report

        Returns:
            Path to the generated PDF report
        """
        # Check if PDF generation is available
        if not PDF_AVAILABLE:
            print("PDF generation not available. Install ReportLab with: pip install reportlab")
            return ""

        # Extract basic information
        doc1_id = comparison_data.get("doc1_id", "Unknown")
        doc2_id = comparison_data.get("doc2_id", "Unknown")
        doc1_date = comparison_data.get("doc1_date", "Unknown")
        doc2_date = comparison_data.get("doc2_date", "Unknown")

        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()

        # Create custom styles
        title_style = styles["Title"]
        heading_style = styles["Heading1"]
        subheading_style = styles["Heading2"]
        normal_style = styles["Normal"]

        # Create positive and negative styles
        positive_style = ParagraphStyle(
            "Positive",
            parent=normal_style,
            textColor=colors.green
        )
        negative_style = ParagraphStyle(
            "Negative",
            parent=normal_style,
            textColor=colors.red
        )

        # Create document elements
        elements = []

        # Add title
        elements.append(Paragraph("Financial Document Comparison Report", title_style))
        elements.append(Spacer(1, 0.25 * inch))

        # Add document information
        elements.append(Paragraph("Document Information", heading_style))
        elements.append(Paragraph(f"Document 1: {doc1_id} ({doc1_date})", normal_style))
        elements.append(Paragraph(f"Document 2: {doc2_id} ({doc2_date})", normal_style))
        elements.append(Spacer(1, 0.25 * inch))

        # Add time between documents
        time_between = comparison_data.get("time_between_documents", {})
        if time_between:
            days = time_between.get("days")
            months = time_between.get("months")
            years = time_between.get("years")

            if days is not None:
                elements.append(Paragraph(
                    f"Time Between Documents: {days} days ({months} months, {years:.2f} years)",
                    normal_style
                ))

        # Add chronological order
        order = comparison_data.get("chronological_order")
        if order and order != "unknown":
            order_text = ""
            if order == "chronological":
                order_text = "Documents are in chronological order (Document 1 is older)"
            elif order == "reverse_chronological":
                order_text = "Documents are in reverse chronological order (Document 2 is older)"
            elif order == "same_date":
                order_text = "Documents have the same date"

            elements.append(Paragraph(f"Chronological Order: {order_text}", normal_style))

        elements.append(Spacer(1, 0.25 * inch))

        # Add portfolio summary
        elements.append(Paragraph("Portfolio Summary", heading_style))
        portfolio = comparison_data.get("portfolio_summary", {})

        if portfolio:
            value1 = portfolio.get("value1")
            value2 = portfolio.get("value2")
            absolute_change = portfolio.get("absolute_change")
            percentage_change = portfolio.get("percentage_change")
            annualized_return = portfolio.get("annualized_return")

            if value1 is not None and value2 is not None:
                elements.append(Paragraph(f"Document 1 Value: ${value1:,.2f}", normal_style))
                elements.append(Paragraph(f"Document 2 Value: ${value2:,.2f}", normal_style))

                if absolute_change is not None:
                    style = positive_style if absolute_change > 0 else negative_style
                    elements.append(Paragraph(f"Absolute Change: ${absolute_change:,.2f}", style))

                    if percentage_change is not None:
                        elements.append(Paragraph(f"Percentage Change: {percentage_change:.2f}%", style))

                if annualized_return is not None:
                    style = positive_style if annualized_return > 0 else negative_style
                    elements.append(Paragraph(f"Annualized Return: {annualized_return:.2f}%", style))

        elements.append(Spacer(1, 0.25 * inch))

        # Add asset allocation changes
        elements.append(Paragraph("Asset Allocation Changes", heading_style))
        asset_allocation = comparison_data.get("asset_allocation_changes", {})

        if asset_allocation:
            # Create table data
            table_data = [
                ["Asset Class", "Doc 1 Value", "Doc 2 Value", "Value Change", "Doc 1 %", "Doc 2 %", "% Point Change"]
            ]

            for asset_class, data in asset_allocation.items():
                value1 = data.get("value1", 0)
                value2 = data.get("value2", 0)
                value_change = data.get("value_change", 0)
                percentage1 = data.get("percentage1", 0)
                percentage2 = data.get("percentage2", 0)
                percentage_point_change = data.get("percentage_point_change", 0)

                table_data.append([
                    asset_class,
                    f"${value1:,.2f}",
                    f"${value2:,.2f}",
                    f"${value_change:,.2f}",
                    f"{percentage1:.2f}%",
                    f"{percentage2:.2f}%",
                    f"{percentage_point_change:.2f}%"
                ])

            # Create table
            table = Table(table_data)

            # Add table style
            table_style = TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                ("ALIGN", (0, 1), (0, -1), "LEFT"),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ])

            # Add conditional formatting for value changes
            for i in range(1, len(table_data)):
                value_change = data.get("value_change", 0)
                if value_change > 0:
                    table_style.add("TEXTCOLOR", (3, i), (3, i), colors.green)
                elif value_change < 0:
                    table_style.add("TEXTCOLOR", (3, i), (3, i), colors.red)

                pp_change = data.get("percentage_point_change", 0)
                if pp_change > 0:
                    table_style.add("TEXTCOLOR", (6, i), (6, i), colors.green)
                elif pp_change < 0:
                    table_style.add("TEXTCOLOR", (6, i), (6, i), colors.red)

            table.setStyle(table_style)
            elements.append(table)

        elements.append(Spacer(1, 0.25 * inch))

        # Add top gainers
        elements.append(Paragraph("Top Gainers", heading_style))
        top_gainers = comparison_data.get("top_gainers", [])

        if top_gainers:
            # Create table data
            table_data = [
                ["Security", "ISIN", "Doc 1 Value", "Doc 2 Value", "Value Change", "% Change"]
            ]

            for security in top_gainers[:5]:  # Limit to top 5
                description = security.get("description", "Unknown")
                isin = security.get("isin", "N/A")
                valuation1 = security.get("valuation1", 0)
                valuation2 = security.get("valuation2", 0)
                valuation_change = security.get("valuation_change", 0)
                percentage_change = security.get("percentage_change", 0)

                table_data.append([
                    description,
                    isin,
                    f"${valuation1:,.2f}",
                    f"${valuation2:,.2f}",
                    f"${valuation_change:,.2f}",
                    f"{percentage_change:.2f}%"
                ])

            # Create table
            table = Table(table_data)

            # Add table style
            table_style = TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                ("ALIGN", (0, 1), (1, -1), "LEFT"),
                ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ])

            # Add conditional formatting for value changes
            for i in range(1, len(table_data)):
                table_style.add("TEXTCOLOR", (4, i), (5, i), colors.green)

            table.setStyle(table_style)
            elements.append(table)

        elements.append(Spacer(1, 0.25 * inch))

        # Add top losers
        elements.append(Paragraph("Top Losers", heading_style))
        top_losers = comparison_data.get("top_losers", [])

        if top_losers:
            # Create table data
            table_data = [
                ["Security", "ISIN", "Doc 1 Value", "Doc 2 Value", "Value Change", "% Change"]
            ]

            for security in top_losers[:5]:  # Limit to top 5
                description = security.get("description", "Unknown")
                isin = security.get("isin", "N/A")
                valuation1 = security.get("valuation1", 0)
                valuation2 = security.get("valuation2", 0)
                valuation_change = security.get("valuation_change", 0)
                percentage_change = security.get("percentage_change", 0)

                table_data.append([
                    description,
                    isin,
                    f"${valuation1:,.2f}",
                    f"${valuation2:,.2f}",
                    f"${valuation_change:,.2f}",
                    f"{percentage_change:.2f}%"
                ])

            # Create table
            table = Table(table_data)

            # Add table style
            table_style = TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                ("ALIGN", (0, 1), (1, -1), "LEFT"),
                ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ])

            # Add conditional formatting for value changes
            for i in range(1, len(table_data)):
                table_style.add("TEXTCOLOR", (4, i), (5, i), colors.red)

            table.setStyle(table_style)
            elements.append(table)

        # Add footer
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(Paragraph(
            f"Generated by Financial Document Analyzer on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles["Italic"]
        ))

        # Build PDF
        doc.build(elements)

        print(f"PDF report saved to: {output_path}")
        return output_path

def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate reports from financial document comparison data.")
    parser.add_argument("--comparison-file", required=True, help="Path to comparison data JSON file")
    parser.add_argument("--output-dir", required=True, help="Directory to save reports")
    parser.add_argument("--format", choices=["html", "csv", "all"], default="all", help="Report format")

    args = parser.parse_args()

    # Load comparison data
    with open(args.comparison_file, "r", encoding="utf-8") as f:
        comparison_data = json.load(f)

    # Create report generator
    generator = ReportGenerator()

    # Generate reports
    if args.format in ["html", "all"]:
        html_path = os.path.join(args.output_dir, "comparison_report.html")
        generator.generate_html_report(comparison_data, html_path)

    if args.format in ["csv", "all"]:
        generator.export_to_csv(comparison_data, args.output_dir)

    return 0

if __name__ == "__main__":
    main()
