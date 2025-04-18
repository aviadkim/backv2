"""
Table Detector Agent for the RAG Multimodal Financial Document Processor.
"""

import os
import logging
import numpy as np
import cv2
from PIL import Image
import re
from typing import List, Dict, Any, Optional, Tuple

from ..utils import ensure_dir, visualize_extraction

logger = logging.getLogger(__name__)

class TableDetectorAgent:
    """
    Table Detector Agent for detecting and extracting tables from documents.
    """
    
    def __init__(self, config):
        """
        Initialize the Table Detector Agent.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.table_config = config["table_detection"]
        self.output_config = config["output"]
        
        logger.info("Initialized Table Detector Agent")
    
    def process(self, pdf_path: str, ocr_results: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
        """
        Process a PDF document to detect and extract tables.
        
        Args:
            pdf_path: Path to the PDF file
            ocr_results: OCR results
            output_dir: Output directory
            
        Returns:
            Dictionary with table detection results
        """
        logger.info(f"Processing {pdf_path} for table detection")
        
        # Create output directory
        tables_dir = os.path.join(output_dir, "tables")
        ensure_dir(tables_dir)
        
        # Extract tables using multiple methods
        tables_camelot = self._extract_tables_camelot(pdf_path)
        tables_pdfplumber = self._extract_tables_pdfplumber(pdf_path)
        tables_vision = self._extract_tables_vision(ocr_results, tables_dir)
        
        # Combine results
        all_tables = self._combine_tables(tables_camelot, tables_pdfplumber, tables_vision)
        
        # Save results
        self._save_tables(all_tables, tables_dir)
        
        logger.info(f"Table detection complete, found {len(all_tables)} tables")
        
        return {
            "tables": all_tables,
            "tables_dir": tables_dir
        }
    
    def _extract_tables_camelot(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract tables using Camelot.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of tables
        """
        logger.info("Extracting tables with Camelot")
        
        tables = []
        
        try:
            try:
                import camelot
                
                # Extract tables with lattice method
                lattice_tables = camelot.read_pdf(
                    pdf_path,
                    pages="all",
                    flavor="lattice",
                    suppress_stdout=True
                )
                
                logger.info(f"Found {len(lattice_tables)} tables with lattice method")
                
                # Extract tables with stream method
                stream_tables = camelot.read_pdf(
                    pdf_path,
                    pages="all",
                    flavor="stream",
                    suppress_stdout=True,
                    edge_tol=50,
                    row_tol=10
                )
                
                logger.info(f"Found {len(stream_tables)} tables with stream method")
                
                # Process lattice tables
                for i, table in enumerate(lattice_tables):
                    if table.accuracy > 80:  # Only include high-accuracy tables
                        tables.append({
                            "id": f"lattice_{i+1}",
                            "page": table.page,
                            "accuracy": table.accuracy,
                            "method": "camelot_lattice",
                            "data": table.df.to_dict(orient="records"),
                            "headers": table.df.columns.tolist(),
                            "rows": table.df.values.tolist()
                        })
                
                # Process stream tables
                for i, table in enumerate(stream_tables):
                    # Check if this table is likely a duplicate of one we already have
                    is_duplicate = False
                    for existing_table in tables:
                        if self._is_similar_table(table.df, existing_table["rows"], existing_table["headers"]):
                            is_duplicate = True
                            break
                    
                    if not is_duplicate and table.accuracy > 70:  # Lower threshold for stream
                        tables.append({
                            "id": f"stream_{i+1}",
                            "page": table.page,
                            "accuracy": table.accuracy,
                            "method": "camelot_stream",
                            "data": table.df.to_dict(orient="records"),
                            "headers": table.df.columns.tolist(),
                            "rows": table.df.values.tolist()
                        })
            except (ImportError, NameError) as e:
                logger.warning(f"Camelot not available: {e}")
                
                # Try to use tabula-py as fallback
                try:
                    import tabula
                    logger.info("Falling back to tabula-py for table extraction")
                    
                    # Extract tables
                    tabula_tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
                    
                    logger.info(f"Found {len(tabula_tables)} tables with tabula-py")
                    
                    # Process tables
                    for i, df in enumerate(tabula_tables):
                        if not df.empty:
                            tables.append({
                                "id": f"tabula_{i+1}",
                                "page": i + 1,  # Approximate page number
                                "accuracy": 75,  # Arbitrary accuracy for tabula
                                "method": "tabula",
                                "data": df.to_dict(orient="records"),
                                "headers": df.columns.tolist(),
                                "rows": df.values.tolist()
                            })
                except ImportError:
                    logger.warning("tabula-py not available")
        except Exception as e:
            logger.error(f"Error extracting tables: {e}")
        
        return tables
    
    def _extract_tables_pdfplumber(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract tables using pdfplumber.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of tables
        """
        logger.info("Extracting tables with pdfplumber")
        
        tables = []
        
        try:
            import pdfplumber
            
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables()
                    
                    for j, table_data in enumerate(page_tables):
                        if not table_data or len(table_data) <= 1:
                            continue
                        
                        # Convert to pandas DataFrame format
                        headers = table_data[0]
                        rows = table_data[1:]
                        
                        # Check if this table is likely a duplicate of one we already have
                        is_duplicate = False
                        for existing_table in tables:
                            if self._is_similar_table(rows, existing_table["rows"], existing_table["headers"]):
                                is_duplicate = True
                                break
                        
                        if not is_duplicate:
                            tables.append({
                                "id": f"pdfplumber_{i+1}_{j+1}",
                                "page": i + 1,
                                "accuracy": 80,  # Arbitrary accuracy for pdfplumber
                                "method": "pdfplumber",
                                "data": [dict(zip(headers, row)) for row in rows],
                                "headers": headers,
                                "rows": rows
                            })
        except Exception as e:
            logger.error(f"Error extracting tables with pdfplumber: {e}")
        
        return tables
    
    def _extract_tables_vision(self, ocr_results: Dict[str, Any], output_dir: str) -> List[Dict[str, Any]]:
        """
        Extract tables using computer vision techniques.
        
        Args:
            ocr_results: OCR results
            output_dir: Output directory
            
        Returns:
            List of tables
        """
        logger.info("Extracting tables with computer vision")
        
        tables = []
        
        try:
            # Process each page
            for page_result in ocr_results["pages"]:
                page_num = page_result["page"]
                
                # Get image path
                image_path = None
                for path in ocr_results.get("image_paths", []):
                    if f"page_{page_num}_" in path:
                        image_path = path
                        break
                
                if not image_path:
                    continue
                
                # Load image
                image = cv2.imread(image_path)
                if image is None:
                    continue
                
                # Convert to grayscale
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                
                # Apply threshold
                _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
                
                # Detect horizontal lines
                horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (self.table_config["line_length"], 1))
                horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=3)
                
                # Detect vertical lines
                vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, self.table_config["line_length"]))
                vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=3)
                
                # Combine lines
                table_mask = cv2.add(horizontal_lines, vertical_lines)
                
                # Find contours
                contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                # Filter contours by size
                min_area = image.shape[0] * image.shape[1] * 0.01  # At least 1% of the image
                table_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]
                
                # Process each table contour
                for i, contour in enumerate(table_contours):
                    # Get bounding box
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Visualize table
                    if self.output_config["save_visualizations"]:
                        vis_image = image.copy()
                        cv2.rectangle(vis_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.imwrite(os.path.join(output_dir, f"table_vision_{page_num}_{i+1}.jpg"), vis_image)
                    
                    # Extract words in this region
                    table_words = []
                    for word in page_result["words"]:
                        word_x = word["box"]["x"]
                        word_y = word["box"]["y"]
                        
                        if (x <= word_x <= x + w) and (y <= word_y <= y + h):
                            table_words.append(word)
                    
                    # Group words into rows based on y-coordinate
                    rows = self._group_words_into_rows(table_words)
                    
                    # Extract headers (first row)
                    headers = []
                    if rows:
                        headers = [word["text"] for word in rows[0]]
                        rows = rows[1:]  # Remove header row
                    
                    # Convert rows to table format
                    table_rows = []
                    for row in rows:
                        table_rows.append([word["text"] for word in row])
                    
                    # Add to tables
                    if headers and table_rows:
                        tables.append({
                            "id": f"vision_{page_num}_{i+1}",
                            "page": page_num,
                            "accuracy": 70,  # Arbitrary accuracy for vision
                            "method": "vision",
                            "data": [dict(zip(headers, row)) for row in table_rows],
                            "headers": headers,
                            "rows": table_rows,
                            "bbox": [x, y, x + w, y + h]
                        })
        except Exception as e:
            logger.error(f"Error extracting tables with vision: {e}")
        
        return tables
    
    def _group_words_into_rows(self, words: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Group words into rows based on y-coordinate.
        
        Args:
            words: List of words
            
        Returns:
            List of rows, each containing a list of words
        """
        if not words:
            return []
        
        # Sort words by y-coordinate
        sorted_words = sorted(words, key=lambda w: w["box"]["y"])
        
        # Group words into rows
        rows = []
        current_row = [sorted_words[0]]
        current_y = sorted_words[0]["box"]["y"]
        
        for word in sorted_words[1:]:
            word_y = word["box"]["y"]
            
            # If word is on the same line (within tolerance)
            if abs(word_y - current_y) <= 10:
                current_row.append(word)
            else:
                # Sort words in row by x-coordinate
                current_row.sort(key=lambda w: w["box"]["x"])
                rows.append(current_row)
                
                # Start new row
                current_row = [word]
                current_y = word_y
        
        # Add the last row
        if current_row:
            current_row.sort(key=lambda w: w["box"]["x"])
            rows.append(current_row)
        
        return rows
    
    def _combine_tables(self, tables_camelot: List[Dict[str, Any]], 
                       tables_pdfplumber: List[Dict[str, Any]],
                       tables_vision: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Combine tables from different extraction methods.
        
        Args:
            tables_camelot: Tables from Camelot
            tables_pdfplumber: Tables from pdfplumber
            tables_vision: Tables from vision
            
        Returns:
            Combined list of tables
        """
        # Start with Camelot tables (highest quality)
        combined_tables = tables_camelot.copy()
        
        # Add pdfplumber tables if they provide additional information
        for plumber_table in tables_pdfplumber:
            is_duplicate = False
            for existing_table in combined_tables:
                if self._is_similar_table(plumber_table["rows"], existing_table["rows"], existing_table["headers"]):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                combined_tables.append(plumber_table)
        
        # Add vision tables if they provide additional information
        for vision_table in tables_vision:
            is_duplicate = False
            for existing_table in combined_tables:
                if self._is_similar_table(vision_table["rows"], existing_table["rows"], existing_table["headers"]):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                combined_tables.append(vision_table)
        
        return combined_tables
    
    def _is_similar_table(self, table1, table2, headers2, similarity_threshold: float = 0.7) -> bool:
        """
        Check if two tables are similar.
        
        Args:
            table1: First table
            table2: Second table
            headers2: Headers of the second table
            similarity_threshold: Threshold for considering tables similar
            
        Returns:
            Boolean indicating if tables are similar
        """
        # Handle different input types
        if hasattr(table1, 'shape'):  # pandas DataFrame
            rows1 = table1.values.tolist()
            headers1 = table1.columns.tolist()
        else:
            rows1 = table1
            headers1 = []  # We don't have headers for table1
        
        # If shapes are very different, tables are not similar
        if abs(len(rows1) - len(table2)) > 3:
            return False
        
        # If one table is much smaller than the other, they're not similar
        min_rows = min(len(rows1), len(table2))
        
        if min_rows == 0:
            return False
        
        # Compare content of overlapping cells
        match_count = 0
        total_cells = 0
        
        for i in range(min_rows):
            row1 = rows1[i]
            row2 = table2[i]
            
            min_cols = min(len(row1), len(row2))
            total_cells += min_cols
            
            for j in range(min_cols):
                val1 = str(row1[j]).strip()
                val2 = str(row2[j]).strip()
                
                # Check for exact match or significant overlap
                if val1 == val2 or (len(val1) > 0 and len(val2) > 0 and 
                                    (val1 in val2 or val2 in val1)):
                    match_count += 1
        
        similarity = match_count / total_cells if total_cells > 0 else 0
        return similarity >= similarity_threshold
    
    def _save_tables(self, tables: List[Dict[str, Any]], output_dir: str) -> None:
        """
        Save tables to files.
        
        Args:
            tables: List of tables
            output_dir: Output directory
        """
        # Save all tables to a single JSON file
        import json
        with open(os.path.join(output_dir, "tables.json"), "w", encoding="utf-8") as f:
            json.dump(tables, f, indent=2, ensure_ascii=False)
        
        # Save each table to a CSV file
        import csv
        for table in tables:
            table_id = table["id"]
            headers = table["headers"]
            rows = table["rows"]
            
            with open(os.path.join(output_dir, f"{table_id}.csv"), "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)
