"""
Document Structure Analyzer - Analyzes the structure of financial documents.

This module provides tools to analyze the structure of financial documents,
identifying sections, headers, and hierarchical relationships.
"""
import os
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
import json
from collections import defaultdict

# Import extraction libraries
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logging.warning("pdfplumber library not available. Install with: pip install pdfplumber")

try:
    from unstructured.partition.pdf import partition_pdf
    from unstructured.documents.elements import (
        Table, Text, Title, NarrativeText, ListItem, Header
    )
    UNSTRUCTURED_AVAILABLE = True
except ImportError:
    UNSTRUCTURED_AVAILABLE = False
    logging.warning("Unstructured library not available. Install with: pip install unstructured")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentStructureAnalyzer:
    """
    Analyzes the structure of financial documents to identify sections,
    headers, and hierarchical relationships.
    """
    
    def __init__(self):
        """Initialize the document structure analyzer."""
        self.elements = []
        self.sections = []
        self.document_map = {}
        self.tables = []
        self.text_blocks = []
        self.headers = []
        self.footers = []
        self.page_count = 0
        
    def analyze(self, pdf_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze the structure of a financial document.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save output files (default: None)
        
        Returns:
            Dict containing document structure analysis
        """
        logger.info(f"Analyzing document structure: {pdf_path}")
        
        # Reset data
        self.elements = []
        self.sections = []
        self.document_map = {}
        self.tables = []
        self.text_blocks = []
        self.headers = []
        self.footers = []
        
        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Extract document metadata
            metadata = self._extract_metadata(pdf_path)
            self.page_count = metadata.get("page_count", 0)
            
            # Extract elements using Unstructured
            if UNSTRUCTURED_AVAILABLE:
                self.elements = partition_pdf(
                    pdf_path,
                    extract_images_in_pdf=False,
                    infer_table_structure=True,
                    strategy="hi_res"
                )
                
                # Process elements to identify structure
                self._process_elements()
            
            # Extract page layout using pdfplumber
            if PDFPLUMBER_AVAILABLE:
                self._analyze_page_layout(pdf_path)
            
            # Identify document sections
            self._identify_sections()
            
            # Create document map
            self._create_document_map()
            
            # Save results if output_dir is specified
            if output_dir:
                self._save_results(output_dir)
            
            logger.info("Document structure analysis completed.")
            return self.document_map
            
        except Exception as e:
            logger.error(f"Error analyzing document structure: {str(e)}")
            return {"error": str(e)}
    
    def _extract_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """Extract metadata from the PDF."""
        metadata = {
            "filename": os.path.basename(pdf_path),
            "file_size": os.path.getsize(pdf_path),
            "page_count": 0
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                metadata["page_count"] = len(pdf.pages)
                if hasattr(pdf, "metadata") and pdf.metadata:
                    for key, value in pdf.metadata.items():
                        if key.startswith("/"):
                            key = key[1:]  # Remove leading slash
                        metadata[key] = value
        except Exception as e:
            logger.warning(f"Error extracting metadata: {str(e)}")
        
        return metadata
    
    def _process_elements(self):
        """Process extracted elements to identify structure."""
        # Separate elements by type
        for element in self.elements:
            if isinstance(element, Table):
                self.tables.append({
                    "element": element,
                    "page_number": element.metadata.page_number,
                    "coordinates": self._get_element_coordinates(element),
                    "text": str(element)
                })
            elif isinstance(element, (Text, NarrativeText, ListItem)):
                self.text_blocks.append({
                    "element": element,
                    "page_number": element.metadata.page_number,
                    "coordinates": self._get_element_coordinates(element),
                    "text": str(element)
                })
            elif isinstance(element, (Title, Header)):
                self.headers.append({
                    "element": element,
                    "page_number": element.metadata.page_number,
                    "coordinates": self._get_element_coordinates(element),
                    "text": str(element),
                    "level": self._estimate_header_level(element)
                })
        
        logger.info(f"Processed {len(self.tables)} tables, {len(self.text_blocks)} text blocks, and {len(self.headers)} headers")
    
    def _get_element_coordinates(self, element) -> Dict[str, float]:
        """Get coordinates of an element if available."""
        coordinates = {}
        
        try:
            if hasattr(element.metadata, "coordinates"):
                coords = element.metadata.coordinates
                if coords:
                    coordinates = {
                        "x0": coords.get("x0", 0),
                        "y0": coords.get("y0", 0),
                        "x1": coords.get("x1", 0),
                        "y1": coords.get("y1", 0),
                    }
        except Exception:
            pass
        
        return coordinates
    
    def _estimate_header_level(self, element) -> int:
        """Estimate the level of a header based on font size and style."""
        level = 1  # Default level
        
        try:
            # Check if font size is available
            if hasattr(element.metadata, "font_size") and element.metadata.font_size:
                font_size = element.metadata.font_size
                
                # Estimate level based on font size
                if font_size > 18:
                    level = 1
                elif font_size > 16:
                    level = 2
                elif font_size > 14:
                    level = 3
                elif font_size > 12:
                    level = 4
                else:
                    level = 5
            
            # Check if it's bold
            if hasattr(element.metadata, "font_weight") and element.metadata.font_weight == "bold":
                level = min(level, 3)  # Bold text is likely a header of level 3 or higher
        except Exception:
            pass
        
        return level
    
    def _analyze_page_layout(self, pdf_path: str):
        """Analyze page layout using pdfplumber."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Analyze each page
                for i, page in enumerate(pdf.pages):
                    page_number = i + 1
                    
                    # Extract text from the top of the page (potential header)
                    top_height = page.height * 0.1  # Top 10% of the page
                    top_crop = page.crop((0, 0, page.width, top_height))
                    top_text = top_crop.extract_text() or ""
                    
                    if top_text.strip():
                        self.headers.append({
                            "element": None,
                            "page_number": page_number,
                            "coordinates": {"x0": 0, "y0": 0, "x1": page.width, "y1": top_height},
                            "text": top_text,
                            "level": 0,  # Page header
                            "type": "page_header"
                        })
                    
                    # Extract text from the bottom of the page (potential footer)
                    bottom_height = page.height * 0.1  # Bottom 10% of the page
                    bottom_crop = page.crop((0, page.height - bottom_height, page.width, page.height))
                    bottom_text = bottom_crop.extract_text() or ""
                    
                    if bottom_text.strip():
                        self.footers.append({
                            "element": None,
                            "page_number": page_number,
                            "coordinates": {"x0": 0, "y0": page.height - bottom_height, "x1": page.width, "y1": page.height},
                            "text": bottom_text,
                            "type": "page_footer"
                        })
                    
                    # Detect tables
                    page_tables = page.find_tables()
                    for table in page_tables:
                        # Check if this table is already in self.tables
                        table_bbox = (table.bbox[0], table.bbox[1], table.bbox[2], table.bbox[3])
                        table_already_detected = False
                        
                        for existing_table in self.tables:
                            if existing_table["page_number"] == page_number:
                                existing_coords = existing_table["coordinates"]
                                if existing_coords:
                                    existing_bbox = (
                                        existing_coords.get("x0", 0),
                                        existing_coords.get("y0", 0),
                                        existing_coords.get("x1", 0),
                                        existing_coords.get("y1", 0)
                                    )
                                    
                                    # Check if bounding boxes overlap significantly
                                    overlap = self._calculate_bbox_overlap(table_bbox, existing_bbox)
                                    if overlap > 0.5:  # More than 50% overlap
                                        table_already_detected = True
                                        break
                        
                        if not table_already_detected:
                            # Extract table
                            table_obj = page.crop(table.bbox).extract_table()
                            if table_obj:
                                self.tables.append({
                                    "element": None,
                                    "page_number": page_number,
                                    "coordinates": {
                                        "x0": table.bbox[0],
                                        "y0": table.bbox[1],
                                        "x1": table.bbox[2],
                                        "y1": table.bbox[3]
                                    },
                                    "text": str(table_obj),
                                    "data": table_obj,
                                    "extraction_method": "pdfplumber"
                                })
        
        except Exception as e:
            logger.warning(f"Error analyzing page layout: {str(e)}")
    
    def _calculate_bbox_overlap(self, bbox1, bbox2) -> float:
        """Calculate the overlap between two bounding boxes."""
        # Calculate intersection
        x_left = max(bbox1[0], bbox2[0])
        y_top = max(bbox1[1], bbox2[1])
        x_right = min(bbox1[2], bbox2[2])
        y_bottom = min(bbox1[3], bbox2[3])
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0  # No overlap
        
        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        
        # Calculate areas of both boxes
        bbox1_area = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
        bbox2_area = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
        
        # Calculate overlap as a percentage of the smaller box
        smaller_area = min(bbox1_area, bbox2_area)
        if smaller_area == 0:
            return 0.0
        
        return intersection_area / smaller_area
    
    def _identify_sections(self):
        """Identify document sections based on headers and content."""
        # Sort headers by page number and position
        sorted_headers = sorted(
            self.headers,
            key=lambda h: (h["page_number"], h["coordinates"].get("y0", 0) if h["coordinates"] else 0)
        )
        
        # Group text blocks by page
        text_by_page = defaultdict(list)
        for block in self.text_blocks:
            text_by_page[block["page_number"]].append(block)
        
        # Group tables by page
        tables_by_page = defaultdict(list)
        for table in self.tables:
            tables_by_page[table["page_number"]].append(table)
        
        # Create sections based on headers
        current_section = None
        
        for i, header in enumerate(sorted_headers):
            # Skip page headers
            if header.get("type") == "page_header":
                continue
            
            # Create a new section
            section = {
                "title": header["text"],
                "level": header["level"],
                "page_number": header["page_number"],
                "start_coordinates": header["coordinates"],
                "end_coordinates": None,
                "content": [],
                "tables": [],
                "subsections": []
            }
            
            # Determine the end of this section (next header or end of document)
            if i < len(sorted_headers) - 1:
                next_header = sorted_headers[i + 1]
                if next_header["page_number"] == header["page_number"]:
                    # Next header is on the same page
                    section["end_coordinates"] = next_header["coordinates"]
                    
                    # Add text blocks between this header and the next
                    for block in text_by_page[header["page_number"]]:
                        block_y0 = block["coordinates"].get("y0", 0) if block["coordinates"] else 0
                        header_y1 = header["coordinates"].get("y1", 0) if header["coordinates"] else 0
                        next_header_y0 = next_header["coordinates"].get("y0", 0) if next_header["coordinates"] else float('inf')
                        
                        if header_y1 <= block_y0 < next_header_y0:
                            section["content"].append(block)
                    
                    # Add tables between this header and the next
                    for table in tables_by_page[header["page_number"]]:
                        table_y0 = table["coordinates"].get("y0", 0) if table["coordinates"] else 0
                        header_y1 = header["coordinates"].get("y1", 0) if header["coordinates"] else 0
                        next_header_y0 = next_header["coordinates"].get("y0", 0) if next_header["coordinates"] else float('inf')
                        
                        if header_y1 <= table_y0 < next_header_y0:
                            section["tables"].append(table)
                else:
                    # Next header is on a different page
                    # Add all remaining content on this page
                    for block in text_by_page[header["page_number"]]:
                        block_y0 = block["coordinates"].get("y0", 0) if block["coordinates"] else 0
                        header_y1 = header["coordinates"].get("y1", 0) if header["coordinates"] else 0
                        
                        if block_y0 >= header_y1:
                            section["content"].append(block)
                    
                    # Add all remaining tables on this page
                    for table in tables_by_page[header["page_number"]]:
                        table_y0 = table["coordinates"].get("y0", 0) if table["coordinates"] else 0
                        header_y1 = header["coordinates"].get("y1", 0) if header["coordinates"] else 0
                        
                        if table_y0 >= header_y1:
                            section["tables"].append(table)
                    
                    # Add content from pages between this header and the next
                    for page_num in range(header["page_number"] + 1, next_header["page_number"]):
                        section["content"].extend(text_by_page[page_num])
                        section["tables"].extend(tables_by_page[page_num])
            else:
                # This is the last header, add all remaining content
                for page_num in range(header["page_number"], self.page_count + 1):
                    # Add text blocks after this header on the same page
                    if page_num == header["page_number"]:
                        for block in text_by_page[page_num]:
                            block_y0 = block["coordinates"].get("y0", 0) if block["coordinates"] else 0
                            header_y1 = header["coordinates"].get("y1", 0) if header["coordinates"] else 0
                            
                            if block_y0 >= header_y1:
                                section["content"].append(block)
                        
                        # Add tables after this header on the same page
                        for table in tables_by_page[page_num]:
                            table_y0 = table["coordinates"].get("y0", 0) if table["coordinates"] else 0
                            header_y1 = header["coordinates"].get("y1", 0) if header["coordinates"] else 0
                            
                            if table_y0 >= header_y1:
                                section["tables"].append(table)
                    else:
                        # Add all content from subsequent pages
                        section["content"].extend(text_by_page[page_num])
                        section["tables"].extend(tables_by_page[page_num])
            
            # Add the section to the list
            self.sections.append(section)
            
            # Update current section
            current_section = section
        
        # Handle content not associated with any header
        unassigned_content = []
        unassigned_tables = []
        
        for page_num in range(1, self.page_count + 1):
            # Check if this page has any headers
            page_has_header = any(h["page_number"] == page_num for h in sorted_headers if h.get("type") != "page_header")
            
            if not page_has_header:
                # Add all content from this page to unassigned
                unassigned_content.extend(text_by_page[page_num])
                unassigned_tables.extend(tables_by_page[page_num])
        
        # If there's unassigned content, create a default section
        if unassigned_content or unassigned_tables:
            default_section = {
                "title": "Untitled Section",
                "level": 0,
                "page_number": 1,
                "start_coordinates": None,
                "end_coordinates": None,
                "content": unassigned_content,
                "tables": unassigned_tables,
                "subsections": []
            }
            
            self.sections.append(default_section)
        
        logger.info(f"Identified {len(self.sections)} document sections")
    
    def _create_document_map(self):
        """Create a hierarchical document map."""
        # Sort sections by page number and level
        sorted_sections = sorted(
            self.sections,
            key=lambda s: (s["page_number"], s["level"])
        )
        
        # Create a hierarchical structure
        root_sections = []
        section_stack = []
        
        for section in sorted_sections:
            # Process section level
            while section_stack and section_stack[-1]["level"] >= section["level"]:
                section_stack.pop()
            
            if section_stack:
                # Add as subsection to the parent
                section_stack[-1]["subsections"].append(section)
            else:
                # Add as root section
                root_sections.append(section)
            
            # Add to stack
            section_stack.append(section)
        
        # Create document map
        self.document_map = {
            "title": "Document Structure Map",
            "page_count": self.page_count,
            "section_count": len(self.sections),
            "table_count": len(self.tables),
            "text_block_count": len(self.text_blocks),
            "header_count": len(self.headers),
            "footer_count": len(self.footers),
            "sections": root_sections
        }
        
        # Identify financial sections
        self._identify_financial_sections()
        
        logger.info("Created document map with hierarchical structure")
    
    def _identify_financial_sections(self):
        """Identify financial sections in the document."""
        financial_sections = {
            "portfolio_summary": None,
            "asset_allocation": None,
            "securities": None,
            "bonds": None,
            "equities": None,
            "structured_products": None,
            "cash_accounts": None,
            "performance": None
        }
        
        # Keywords for each section type
        section_keywords = {
            "portfolio_summary": ["portfolio summary", "portfolio overview", "portfolio total", "total assets"],
            "asset_allocation": ["asset allocation", "asset class", "allocation overview"],
            "securities": ["securities", "security overview", "holdings", "positions"],
            "bonds": ["bonds", "fixed income", "debt securities"],
            "equities": ["equities", "stocks", "shares"],
            "structured_products": ["structured products", "structured notes", "certificates"],
            "cash_accounts": ["cash accounts", "liquidity", "cash positions"],
            "performance": ["performance", "profit and loss", "p&l", "returns"]
        }
        
        # Search for financial sections
        for section in self.sections:
            section_text = section["title"].lower()
            
            for section_type, keywords in section_keywords.items():
                if any(keyword in section_text for keyword in keywords):
                    financial_sections[section_type] = {
                        "title": section["title"],
                        "page_number": section["page_number"],
                        "tables": len(section["tables"]),
                        "content_length": len(section["content"])
                    }
                    break
            
            # Also check tables in this section
            for table in section["tables"]:
                table_text = table.get("text", "").lower()
                
                for section_type, keywords in section_keywords.items():
                    if any(keyword in table_text for keyword in keywords):
                        if not financial_sections[section_type]:
                            financial_sections[section_type] = {
                                "title": section["title"],
                                "page_number": section["page_number"],
                                "tables": len(section["tables"]),
                                "content_length": len(section["content"])
                            }
                        break
        
        # Add financial sections to document map
        self.document_map["financial_sections"] = financial_sections
        
        # Count identified financial sections
        identified_count = sum(1 for section in financial_sections.values() if section is not None)
        logger.info(f"Identified {identified_count} financial sections")
    
    def _save_results(self, output_dir):
        """Save analysis results."""
        # Save document map as JSON
        map_path = os.path.join(output_dir, "document_map.json")
        
        # Create a serializable version of the document map
        serializable_map = self._create_serializable_map()
        
        with open(map_path, "w", encoding="utf-8") as f:
            json.dump(serializable_map, f, indent=2)
        
        logger.info(f"Saved document map to {map_path}")
    
    def _create_serializable_map(self) -> Dict[str, Any]:
        """Create a serializable version of the document map."""
        # Create a deep copy of the document map
        serializable_map = dict(self.document_map)
        
        # Process sections recursively
        if "sections" in serializable_map:
            serializable_map["sections"] = self._process_sections_for_serialization(serializable_map["sections"])
        
        return serializable_map
    
    def _process_sections_for_serialization(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process sections for serialization."""
        serializable_sections = []
        
        for section in sections:
            # Create a copy of the section
            serializable_section = dict(section)
            
            # Process content
            if "content" in serializable_section:
                serializable_section["content"] = [
                    {
                        "text": item.get("text", ""),
                        "page_number": item.get("page_number", 0)
                    }
                    for item in serializable_section["content"]
                ]
            
            # Process tables
            if "tables" in serializable_section:
                serializable_section["tables"] = [
                    {
                        "page_number": item.get("page_number", 0),
                        "extraction_method": item.get("extraction_method", "unknown")
                    }
                    for item in serializable_section["tables"]
                ]
            
            # Process subsections recursively
            if "subsections" in serializable_section:
                serializable_section["subsections"] = self._process_sections_for_serialization(serializable_section["subsections"])
            
            # Remove element references
            if "element" in serializable_section:
                del serializable_section["element"]
            
            serializable_sections.append(serializable_section)
        
        return serializable_sections
    
    def get_section_by_type(self, section_type: str) -> Optional[Dict[str, Any]]:
        """
        Get a section by its type.
        
        Args:
            section_type: Type of section to retrieve
        
        Returns:
            Section data or None if not found
        """
        if not self.document_map or "financial_sections" not in self.document_map:
            return None
        
        financial_sections = self.document_map["financial_sections"]
        if section_type in financial_sections and financial_sections[section_type]:
            # Find the full section data
            section_title = financial_sections[section_type]["title"]
            section_page = financial_sections[section_type]["page_number"]
            
            for section in self.sections:
                if section["title"] == section_title and section["page_number"] == section_page:
                    return section
        
        return None
    
    def get_tables_by_section_type(self, section_type: str) -> List[Dict[str, Any]]:
        """
        Get tables from a specific section type.
        
        Args:
            section_type: Type of section to retrieve tables from
        
        Returns:
            List of tables or empty list if not found
        """
        section = self.get_section_by_type(section_type)
        if section and "tables" in section:
            return section["tables"]
        
        return []
    
    def get_content_by_section_type(self, section_type: str) -> List[Dict[str, Any]]:
        """
        Get content from a specific section type.
        
        Args:
            section_type: Type of section to retrieve content from
        
        Returns:
            List of content blocks or empty list if not found
        """
        section = self.get_section_by_type(section_type)
        if section and "content" in section:
            return section["content"]
        
        return []

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze the structure of financial documents.")
    parser.add_argument("file_path", help="Path to the financial document")
    parser.add_argument("--output-dir", help="Directory to save output files")
    
    args = parser.parse_args()
    
    # Check if the file exists
    if not os.path.exists(args.file_path):
        logger.error(f"Error: File not found: {args.file_path}")
        return 1
    
    # Analyze the document
    analyzer = DocumentStructureAnalyzer()
    document_map = analyzer.analyze(args.file_path, output_dir=args.output_dir)
    
    # Print summary
    print("\nDocument Structure Analysis Summary:")
    print("===================================")
    print(f"Page Count: {document_map.get('page_count', 0)}")
    print(f"Section Count: {document_map.get('section_count', 0)}")
    print(f"Table Count: {document_map.get('table_count', 0)}")
    print(f"Text Block Count: {document_map.get('text_block_count', 0)}")
    print(f"Header Count: {document_map.get('header_count', 0)}")
    print(f"Footer Count: {document_map.get('footer_count', 0)}")
    
    # Print financial sections
    if "financial_sections" in document_map:
        print("\nFinancial Sections:")
        print("-----------------")
        for section_type, section_data in document_map["financial_sections"].items():
            if section_data:
                print(f"{section_type}: {section_data['title']} (Page {section_data['page_number']})")
            else:
                print(f"{section_type}: Not found")
    
    return 0

if __name__ == "__main__":
    main()
