"""
Utility functions for the RAG Multimodal Financial Document Processor.
"""

import os
import re
import json
import logging
import numpy as np
import cv2
from PIL import Image
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Tuple, Optional, Union

logger = logging.getLogger(__name__)

def ensure_dir(directory):
    """
    Ensure a directory exists.
    
    Args:
        directory: Directory path
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_json(data, file_path):
    """
    Save data as JSON.
    
    Args:
        data: Data to save
        file_path: File path
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_json(file_path):
    """
    Load data from JSON.
    
    Args:
        file_path: File path
        
    Returns:
        Loaded data
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_isins(text):
    """
    Extract ISINs from text.
    
    Args:
        text: Text to extract ISINs from
        
    Returns:
        List of ISINs
    """
    isin_pattern = r'[A-Z]{2}[A-Z0-9]{9}[0-9]'
    isins = re.findall(isin_pattern, text)
    return list(set(isins))  # Remove duplicates

def extract_numbers(text):
    """
    Extract numbers from text.
    
    Args:
        text: Text to extract numbers from
        
    Returns:
        List of numbers
    """
    # Match numbers with commas, periods, and apostrophes (used as thousand separators)
    number_pattern = r'[\d,\'\.]+(?:\s*%)?'
    numbers = re.findall(number_pattern, text)
    
    # Clean and convert to float
    cleaned_numbers = []
    for num in numbers:
        # Remove non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d\.]', '', num.replace(',', '.').replace("'", ''))
        try:
            cleaned_numbers.append(float(cleaned))
        except ValueError:
            pass
    
    return cleaned_numbers

def parse_numeric_value(value_str):
    """
    Parse a numeric value from a string.
    
    Args:
        value_str: String to parse
        
    Returns:
        Parsed numeric value
    """
    if not value_str:
        return None
    
    # Remove non-numeric characters except decimal point
    cleaned = re.sub(r'[^\d\.]', '', value_str.replace(',', '.').replace("'", ''))
    
    try:
        return float(cleaned)
    except ValueError:
        return None

def find_context(text, target, window=100):
    """
    Find context around a target string.
    
    Args:
        text: Text to search
        target: Target string
        window: Context window size
        
    Returns:
        Context around target
    """
    index = text.find(target)
    if index == -1:
        return ""
    
    start = max(0, index - window)
    end = min(len(text), index + len(target) + window)
    
    return text[start:end]

def visualize_extraction(image, boxes, labels, output_path):
    """
    Visualize extraction results on an image.
    
    Args:
        image: Image to visualize on
        boxes: Bounding boxes
        labels: Labels for boxes
        output_path: Output path for visualization
    """
    # Convert PIL image to OpenCV format if needed
    if isinstance(image, Image.Image):
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    else:
        image_cv = image.copy()
    
    # Draw boxes and labels
    for (box, label) in zip(boxes, labels):
        x1, y1, x2, y2 = box
        cv2.rectangle(image_cv, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image_cv, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Save visualization
    cv2.imwrite(output_path, image_cv)

def calculate_accuracy(extracted_data, expected_data):
    """
    Calculate accuracy of extraction.
    
    Args:
        extracted_data: Extracted data
        expected_data: Expected data
        
    Returns:
        Accuracy metrics
    """
    metrics = {}
    
    # ISIN count accuracy
    if 'isin_count' in expected_data and 'securities' in extracted_data:
        extracted_count = len(extracted_data['securities'])
        expected_count = expected_data['isin_count']
        metrics['isin_count_accuracy'] = min(1.0, extracted_count / expected_count if expected_count > 0 else 0)
    
    # Total value accuracy
    if 'total_value' in expected_data and 'total_value' in extracted_data:
        extracted_value = extracted_data['total_value']
        expected_value = expected_data['total_value']
        metrics['total_value_accuracy'] = 1.0 - min(1.0, abs(extracted_value - expected_value) / expected_value if expected_value > 0 else 0)
    
    # Asset class accuracy
    if 'asset_classes' in expected_data and 'asset_allocation' in extracted_data:
        expected_classes = set(expected_data['asset_classes'])
        extracted_classes = set(extracted_data['asset_allocation'].keys())
        
        if expected_classes:
            metrics['asset_class_accuracy'] = len(expected_classes.intersection(extracted_classes)) / len(expected_classes)
        else:
            metrics['asset_class_accuracy'] = 0.0
    
    # Calculate overall accuracy
    if metrics:
        metrics['overall_accuracy'] = sum(metrics.values()) / len(metrics)
    else:
        metrics['overall_accuracy'] = 0.0
    
    return metrics

def format_currency(value, currency="USD"):
    """
    Format a value as currency.
    
    Args:
        value: Value to format
        currency: Currency code
        
    Returns:
        Formatted currency string
    """
    if value is None:
        return "N/A"
    
    return f"{value:,.2f} {currency}"

def is_valid_isin(isin):
    """
    Check if an ISIN is valid.
    
    Args:
        isin: ISIN to check
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(isin, str):
        return False
    
    # Basic format check: 12 characters, first 2 are letters
    if len(isin) != 12 or not isin[:2].isalpha() or not isin[2:].isalnum():
        return False
    
    # TODO: Implement checksum validation if needed
    
    return True
