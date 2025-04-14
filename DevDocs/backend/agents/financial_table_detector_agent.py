"""
Financial Table Detector Agent for identifying and extracting tables from financial documents.
"""
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import pytesseract
import re
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
from .base_agent import BaseAgent

class FinancialTableDetectorAgent(BaseAgent):
    """Agent for identifying and extracting tables from financial documents."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        lang: str = "heb+eng",
        **kwargs
    ):
        """
        Initialize the financial table detector agent.

        Args:
            api_key: OpenRouter API key
            lang: OCR language (default: "heb+eng")
            **kwargs: Additional parameters for the base agent
        """
        super().__init__(name="Financial Table Detector")
        self.api_key = api_key
        self.description = "I identify and extract tables from financial documents."

        self.lang = lang

        # Common structures of financial tables
        self.table_headers = {
            'balance_sheet': [
                'נכסים', 'התחייבויות', 'הון', 'סך הכל',
                'רכוש קבוע', 'רכוש שוטף', 'מזומנים', 'השקעות'
            ],
            'income_statement': [
                'הכנסות', 'הוצאות', 'רווח', 'הפסד', 'עלות המכר',
                'רווח גולמי', 'רווח תפעולי', 'רווח נקי'
            ],
            'portfolio': [
                'נייר ערך', 'ISIN', 'כמות', 'שער', 'שווי', 'תשואה',
                'עלות', 'רווח', 'אחוז', '%', 'תאריך', 'סוג'
            ]
        }

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task to detect and extract tables from an image.

        Args:
            task: Task dictionary with the following keys:
                - image_path: Path to the image file
                - or
                - image: Image as numpy array

        Returns:
            Dictionary with detected tables and extracted data
        """
        # Get the image
        if 'image_path' in task:
            image_path = task['image_path']
            if isinstance(image_path, str):
                image = cv2.imread(image_path)
            else:
                raise ValueError("image_path must be a string")
        elif 'image' in task:
            image = task['image']
        else:
            raise ValueError("Task must contain either 'image_path' or 'image'")

        # Detect tables
        tables = self.detect_tables(image)

        # Extract data from tables
        results = []
        for table in tables:
            table_data = self.extract_table_data(image, table)
            results.append({
                'region': table,
                'data': table_data
            })

        return {
            'num_tables': len(tables),
            'tables': results
        }

    def detect_tables(self, image):
        """Detect table regions in an image."""
        if isinstance(image, str):
            img = cv2.imread(image)
        else:
            img = image.copy()

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect edges
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # Detect lines (rows and columns in the table)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)

        # Analyze lines to detect table structure
        table_regions = []
        if lines is not None:
            horizontal_lines = []
            vertical_lines = []

            for line in lines:
                x1, y1, x2, y2 = line[0]
                # Calculate line angle
                angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180.0 / np.pi)

                # Sort into horizontal and vertical lines
                if angle < 20:  # Horizontal line
                    horizontal_lines.append((y1, x1, x2))
                elif angle > 70:  # Vertical line
                    vertical_lines.append((x1, y1, y2))

            # Sort lines
            horizontal_lines.sort()
            vertical_lines.sort()

            # Identify table regions by finding intersections of horizontal and vertical lines

            # Simple algorithm to detect table boundaries - can be improved
            if horizontal_lines and vertical_lines:
                # Boundary lines around the table
                top = horizontal_lines[0][0]
                bottom = horizontal_lines[-1][0]
                left = vertical_lines[0][0]
                right = vertical_lines[-1][0]

                # If there are enough lines for a table (at least 3 rows and 2 columns)
                if len(horizontal_lines) >= 3 and len(vertical_lines) >= 2:
                    table_regions.append({
                        'x1': left - 10,  # Margin
                        'y1': top - 10,
                        'x2': right + 10,
                        'y2': bottom + 10,
                        'rows': len(horizontal_lines) - 1,
                        'cols': len(vertical_lines) - 1
                    })

        # Additional approach - text region patterns
        text_regions = self._detect_text_grid_pattern(img)

        # Combine both approaches
        final_regions = self._merge_table_regions(table_regions, text_regions)

        return final_regions

    def _detect_text_grid_pattern(self, img):
        """Detect patterns of text arranged in a grid (table)."""
        # Detect text regions
        data = pytesseract.image_to_data(
            img, lang=self.lang, config='--psm 6',
            output_type=pytesseract.Output.DICT
        )

        # Analyze text layout to detect tabular pattern
        # If there are vertically aligned text lines, it's likely a table

        # Organize data by blocks
        text_blocks = {}
        for i in range(len(data['text'])):
            if data['text'][i].strip():
                block_id = data['block_num'][i]
                if block_id not in text_blocks:
                    text_blocks[block_id] = []
                text_blocks[block_id].append({
                    'text': data['text'][i],
                    'x': data['left'][i],
                    'y': data['top'][i],
                    'w': data['width'][i],
                    'h': data['height'][i]
                })

        # Look for tabular patterns
        table_patterns = []

        # Check if there are at least three blocks with similar vertical alignment
        all_blocks = []
        for block_id, items in text_blocks.items():
            if len(items) >= 3:  # A table needs at least 3 text items
                all_blocks.extend(items)

        if all_blocks:
            # Look for vertical alignment of elements - sign of columns in a table
            x_positions = [item['x'] for item in all_blocks]
            unique_x = set()
            for x in x_positions:
                # Align with error margin
                aligned_x = round(x / 10) * 10
                unique_x.add(aligned_x)

            # If there are at least 2 columns and 3 rows
            if len(unique_x) >= 2:
                # Find table boundaries
                min_x = min(item['x'] for item in all_blocks) - 10
                max_x = max(item['x'] + item['w'] for item in all_blocks) + 10
                min_y = min(item['y'] for item in all_blocks) - 10
                max_y = max(item['y'] + item['h'] for item in all_blocks) + 10

                # Check for financial table keywords
                table_type = self._detect_table_type(all_blocks)

                table_patterns.append({
                    'x1': min_x,
                    'y1': min_y,
                    'x2': max_x,
                    'y2': max_y,
                    'rows': len(set(item['y'] for item in all_blocks)),
                    'cols': len(unique_x),
                    'table_type': table_type
                })

        return table_patterns

    def _detect_table_type(self, text_items):
        """Detect table type based on keywords."""
        all_text = " ".join([item['text'].lower() for item in text_items])

        # Search for keywords
        matches = {}
        for table_type, keywords in self.table_headers.items():
            matches[table_type] = sum(1 for keyword in keywords
                                    if keyword.lower() in all_text)

        # Choose the type with the highest number of matches
        if any(matches.values()):
            return max(matches.items(), key=lambda x: x[1])[0]
        return "unknown"

    def _merge_table_regions(self, line_regions, text_regions):
        """Combine table regions detected by different methods."""
        if not line_regions and not text_regions:
            return []

        # If there's only one type of regions, return it
        if not line_regions:
            return text_regions
        if not text_regions:
            return line_regions

        # Merge overlapping regions
        all_regions = line_regions + text_regions
        merged_regions = []

        # Simple algorithm to merge overlapping regions
        for region in all_regions:
            should_merge = False
            for i, merged in enumerate(merged_regions):
                # Check if there's significant overlap
                overlap_x = max(0, min(region['x2'], merged['x2']) - max(region['x1'], merged['x1']))
                overlap_y = max(0, min(region['y2'], merged['y2']) - max(region['y1'], merged['y1']))

                area_overlap = overlap_x * overlap_y
                area_region = (region['x2'] - region['x1']) * (region['y2'] - region['y1'])
                area_merged = (merged['x2'] - merged['x1']) * (merged['y2'] - merged['y1'])

                # If the overlap is at least 30% of one of the regions
                if area_overlap > 0.3 * min(area_region, area_merged):
                    # Create merged region
                    merged_regions[i] = {
                        'x1': min(region['x1'], merged['x1']),
                        'y1': min(region['y1'], merged['y1']),
                        'x2': max(region['x2'], merged['x2']),
                        'y2': max(region['y2'], merged['y2']),
                        'rows': max(region.get('rows', 0), merged.get('rows', 0)),
                        'cols': max(region.get('cols', 0), merged.get('cols', 0)),
                        'table_type': region.get('table_type', merged.get('table_type', 'unknown'))
                    }
                    should_merge = True
                    break

            if not should_merge:
                merged_regions.append(region)

        return merged_regions

    def extract_table_data(self, img, region):
        """Extract table data from a detected table region."""
        # Crop the table region
        if isinstance(img, str):
            full_img = cv2.imread(img)
        else:
            full_img = img.copy()

        x1, y1, x2, y2 = region['x1'], region['y1'], region['x2'], region['y2']
        table_img = full_img[y1:y2, x1:x2]

        # Enhance table image
        gray = cv2.cvtColor(table_img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

        # Detect horizontal and vertical lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))

        horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel)
        vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel)

        # Combine lines
        table_structure = cv2.add(horizontal_lines, vertical_lines)

        # Detect cells in the table
        contours, _ = cv2.findContours(table_structure, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Sort cells by position (rows and columns)
        cells = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 20 and h > 20:  # Filter out cells that are too small
                cells.append({
                    'x': x, 'y': y, 'w': w, 'h': h,
                    'area': w * h
                })

        # If cell detection failed, try another approach
        if len(cells) < 4:  # A table needs at least 2x2 cells
            return self._extract_with_ocr(table_img)

        # Sort cells by Y coordinate
        cells.sort(key=lambda c: c['y'])

        # Identify rows by grouping cells with similar Y
        rows = []
        current_row = [cells[0]]
        for cell in cells[1:]:
            # If the cell is in the same row (error margin of 10 pixels)
            if abs(cell['y'] - current_row[0]['y']) < 10:
                current_row.append(cell)
            else:
                # Sort cells in the row by X (left to right)
                current_row.sort(key=lambda c: c['x'])
                rows.append(current_row)
                current_row = [cell]

        # Add the last row
        if current_row:
            current_row.sort(key=lambda c: c['x'])
            rows.append(current_row)

        # Extract text from each cell
        table_data = []
        for row in rows:
            row_data = []
            for cell in row:
                # Crop the cell from the image
                cell_img = gray[cell['y']:cell['y']+cell['h'], cell['x']:cell['x']+cell['w']]

                # Extract text from the cell
                text = pytesseract.image_to_string(cell_img, lang=self.lang,
                                                 config='--psm 6')

                # Clean the text
                clean_text = text.strip().replace('\n', ' ')
                row_data.append(clean_text)

            table_data.append(row_data)

        # Create DataFrame from table data
        if table_data and all(len(row) == len(table_data[0]) for row in table_data):
            header = table_data[0]
            data = table_data[1:]
            df = pd.DataFrame(data, columns=header)
            return {
                'type': region.get('table_type', 'unknown'),
                'data': df
            }

        return {
            'type': region.get('table_type', 'unknown'),
            'data': pd.DataFrame(table_data)
        }

    def _extract_with_ocr(self, table_img):
        """Alternative method to extract table data using OCR directly."""
        # Use OCR with table settings
        custom_config = f'--psm 6 -l {self.lang}'
        data = pytesseract.image_to_data(
            table_img, config=custom_config,
            output_type=pytesseract.Output.DICT
        )

        # Organize text by rows
        rows = {}
        for i in range(len(data['text'])):
            if data['text'][i].strip():
                # Group by row (Y with error margin)
                row_key = data['top'][i] // 10
                if row_key not in rows:
                    rows[row_key] = []

                rows[row_key].append({
                    'text': data['text'][i],
                    'x': data['left'][i]
                })

        # Sort data by rows and within each row by X
        table_data = []
        for row_key in sorted(rows.keys()):
            row_items = sorted(rows[row_key], key=lambda x: x['x'])
            table_data.append([item['text'] for item in row_items])

        # If there are enough rows, the first one is the header
        if len(table_data) > 1:
            header = table_data[0]
            data = table_data[1:]

            # Align number of columns
            max_cols = max(len(row) for row in table_data)
            standardized_data = []

            for row in data:
                if len(row) < max_cols:
                    row = row + [''] * (max_cols - len(row))
                standardized_data.append(row[:max_cols])

            # If there are fewer headers than columns
            if len(header) < max_cols:
                header = header + [f'Col{i+1}' for i in range(len(header), max_cols)]

            df = pd.DataFrame(standardized_data, columns=header[:max_cols])
            return {
                'type': 'unknown',
                'data': df
            }

        # If we couldn't identify a table structure
        return {
            'type': 'unknown',
            'data': pd.DataFrame(table_data)
        }
