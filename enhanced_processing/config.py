"""
Configuration module for the RAG Multimodal Financial Document Processor.
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_CONFIG = {
    # OCR Configuration
    "ocr": {
        "languages": ["eng", "heb"],
        "dpi": 300,
        "use_gpu": False,
        "page_segmentation_mode": 1,  # Automatic page segmentation with OSD
        "ocr_engine_mode": 3,  # Default, based on what is available
    },
    
    # Table Detection Configuration
    "table_detection": {
        "min_confidence": 0.7,
        "line_scale": 15,
        "line_length": 100,
        "max_line_gap": 3,
        "threshold_blocksize": 15,
        "threshold_constant": 2,
    },
    
    # Document Processing Configuration
    "document_processing": {
        "extract_tables": True,
        "extract_text": True,
        "extract_images": False,
        "extract_charts": False,
        "extract_headers": True,
        "extract_footers": True,
    },
    
    # RAG Configuration
    "rag": {
        "model": "gpt-4-vision-preview" if OPENAI_API_KEY else "gemini-1.5-pro-vision",
        "temperature": 0.2,
        "max_tokens": 4000,
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "top_k": 5,
    },
    
    # Output Configuration
    "output": {
        "format": "json",
        "save_intermediates": True,
        "save_visualizations": True,
    },
    
    # Expected Values (for validation)
    "expected": {
        "total_value": 19510599,
        "currency": "USD",
        "isin_count": 41,
        "asset_classes": ["Liquidity", "Bonds", "Equities", "Structured products", "Other assets"],
    }
}

def get_config(custom_config=None):
    """
    Get configuration with custom overrides.
    
    Args:
        custom_config: Custom configuration overrides
        
    Returns:
        Merged configuration
    """
    config = DEFAULT_CONFIG.copy()
    
    if custom_config:
        # Merge custom configuration
        for section, section_config in custom_config.items():
            if section in config:
                config[section].update(section_config)
            else:
                config[section] = section_config
    
    return config
