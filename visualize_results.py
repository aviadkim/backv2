#!/usr/bin/env python
"""
Visualization script for the RAG Multimodal Financial Document Processor.
"""

import os
import sys
import argparse
import json
import matplotlib.pyplot as plt
import numpy as np
from pdf2image import convert_from_path
import cv2
from PIL import Image, ImageDraw, ImageFont

def visualize_results(pdf_path, result_path, output_dir):
    """
    Visualize processing results.
    
    Args:
        pdf_path: Path to the PDF file
        result_path: Path to the result JSON file
        output_dir: Output directory
    """
    print(f"Visualizing results for {pdf_path}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Load results
    with open(result_path, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # Convert PDF to images
    images = convert_from_path(pdf_path, dpi=150)
    
    # Save images
    image_paths = []
    for i, image in enumerate(images):
        image_path = os.path.join(output_dir, f"page_{i+1}.jpg")
        image.save(image_path, "JPEG")
        image_paths.append(image_path)
    
    # Visualize securities
    visualize_securities(results, output_dir)
    
    # Visualize asset allocation
    visualize_asset_allocation(results, output_dir)
    
    # Visualize accuracy
    if "accuracy" in results:
        visualize_accuracy(results, output_dir)
    
    # Visualize annotations
    visualize_annotations(results, image_paths, output_dir)
    
    print(f"Visualizations saved to {output_dir}")

def visualize_securities(results, output_dir):
    """
    Visualize securities.
    
    Args:
        results: Results dictionary
        output_dir: Output directory
    """
    securities = results["portfolio"]["securities"]
    
    if not securities:
        return
    
    # Sort securities by value
    securities_sorted = sorted(securities, key=lambda x: x.get("value", 0) or 0, reverse=True)
    
    # Get top 10 securities
    top_securities = securities_sorted[:10]
    
    # Create figure
    plt.figure(figsize=(12, 8))
    
    # Create bar chart
    names = [s.get("name", f"Security {i+1}") for i, s in enumerate(top_securities)]
    values = [s.get("value", 0) or 0 for s in top_securities]
    
    # Truncate long names
    names = [name[:20] + "..." if len(name) > 20 else name for name in names]
    
    # Create bar chart
    bars = plt.bar(names, values)
    
    # Add values on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f"{height:,.0f}",
                ha='center', va='bottom', rotation=0)
    
    # Add labels and title
    plt.xlabel("Security")
    plt.ylabel("Value")
    plt.title("Top 10 Securities by Value")
    
    # Rotate x-axis labels
    plt.xticks(rotation=45, ha='right')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save figure
    plt.savefig(os.path.join(output_dir, "securities.png"))
    plt.close()

def visualize_asset_allocation(results, output_dir):
    """
    Visualize asset allocation.
    
    Args:
        results: Results dictionary
        output_dir: Output directory
    """
    asset_allocation = results["portfolio"]["asset_allocation"]
    
    if not asset_allocation:
        return
    
    # Create figure
    plt.figure(figsize=(10, 8))
    
    # Get asset classes and weights
    asset_classes = list(asset_allocation.keys())
    weights = [allocation.get("weight", 0) or 0 for allocation in asset_allocation.values()]
    
    # Create colors
    colors = plt.cm.tab10(np.arange(len(asset_classes)) % 10)
    
    # Create pie chart
    wedges, texts, autotexts = plt.pie(
        weights, 
        labels=asset_classes, 
        autopct='%1.1f%%',
        colors=colors,
        startangle=90
    )
    
    # Equal aspect ratio ensures that pie is drawn as a circle
    plt.axis('equal')
    
    # Add title
    plt.title("Asset Allocation")
    
    # Save figure
    plt.savefig(os.path.join(output_dir, "asset_allocation.png"))
    plt.close()

def visualize_accuracy(results, output_dir):
    """
    Visualize accuracy metrics.
    
    Args:
        results: Results dictionary
        output_dir: Output directory
    """
    accuracy = results["accuracy"]
    
    if not accuracy:
        return
    
    # Create figure
    plt.figure(figsize=(10, 6))
    
    # Get metrics and values
    metrics = list(accuracy.keys())
    values = list(accuracy.values())
    
    # Create bar chart
    bars = plt.bar(metrics, values)
    
    # Add values on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f"{height:.2f}",
                ha='center', va='bottom', rotation=0)
    
    # Add labels and title
    plt.xlabel("Metric")
    plt.ylabel("Accuracy")
    plt.title("Accuracy Metrics")
    
    # Set y-axis limits
    plt.ylim(0, 1.1)
    
    # Rotate x-axis labels
    plt.xticks(rotation=45, ha='right')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save figure
    plt.savefig(os.path.join(output_dir, "accuracy.png"))
    plt.close()

def visualize_annotations(results, image_paths, output_dir):
    """
    Visualize annotations on PDF images.
    
    Args:
        results: Results dictionary
        image_paths: List of image paths
        output_dir: Output directory
    """
    securities = results["portfolio"]["securities"]
    
    if not securities or not image_paths:
        return
    
    # Create annotations directory
    annotations_dir = os.path.join(output_dir, "annotations")
    os.makedirs(annotations_dir, exist_ok=True)
    
    # Get ISINs
    isins = [s["isin"] for s in securities]
    
    # Process each image
    for i, image_path in enumerate(image_paths):
        # Load image
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        
        # Try to load font
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Convert image to text
        import pytesseract
        text = pytesseract.image_to_string(image)
        
        # Find ISINs in text
        found_isins = []
        for isin in isins:
            if isin in text:
                found_isins.append(isin)
        
        # If no ISINs found, skip this image
        if not found_isins:
            continue
        
        # Get word bounding boxes
        boxes = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        
        # Draw boxes around ISINs
        for isin in found_isins:
            for i, word in enumerate(boxes["text"]):
                if isin in word:
                    x = boxes["left"][i]
                    y = boxes["top"][i]
                    w = boxes["width"][i]
                    h = boxes["height"][i]
                    
                    # Draw rectangle
                    draw.rectangle([x, y, x + w, y + h], outline="red", width=2)
                    
                    # Draw label
                    draw.text((x, y - 20), isin, fill="red", font=font)
        
        # Save annotated image
        annotated_path = os.path.join(annotations_dir, f"annotated_{os.path.basename(image_path)}")
        image.save(annotated_path)

def main():
    """
    Main function to run the script from the command line.
    """
    parser = argparse.ArgumentParser(description='Visualize processing results')
    parser.add_argument('pdf_path', help='Path to the PDF file')
    parser.add_argument('result_path', help='Path to the result JSON file')
    parser.add_argument('--output-dir', help='Output directory')
    
    args = parser.parse_args()
    
    # Set output directory
    output_dir = args.output_dir
    if not output_dir:
        output_dir = os.path.join(os.path.dirname(args.result_path), "visualizations")
    
    # Visualize results
    try:
        visualize_results(args.pdf_path, args.result_path, output_dir)
        sys.exit(0)
    except Exception as e:
        print(f"Error visualizing results: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
