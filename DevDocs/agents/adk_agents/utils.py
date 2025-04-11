"""
Lightweight utility functions for ADK agents.
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Simple response cache to avoid redundant processing
response_cache = {}

def extract_financial_data_simple(document_text: str) -> Dict[str, Any]:
    """
    Extract financial data from document text using a simple approach.
    This is a lightweight version that doesn't require the ADK libraries.

    Args:
        document_text: The text content of a financial document

    Returns:
        Dict[str, Any]: Extracted financial data
    """
    logger.info(f"Extracting financial data using simple method ({len(document_text)} chars)")

    # Simple extraction based on keywords
    metrics = {
        "revenue": None,
        "profit": None,
        "assets": None,
        "liabilities": None,
        "equity": None,
    }

    lines = document_text.split("\n")
    for line in lines:
        line = line.lower().strip()
        for metric in metrics.keys():
            if metric in line:
                # Very simple extraction - find numbers in the line
                import re
                numbers = re.findall(r'\d+(?:\.\d+)?', line)
                if numbers:
                    metrics[metric] = float(numbers[0])

    return {
        "status": "success",
        "extracted_data": {
            "metrics": metrics,
            "confidence": 0.7  # Placeholder confidence score
        }
    }

def analyze_financial_sentiment_simple(text: str) -> Dict[str, Any]:
    """
    Analyze the sentiment of financial text using a simple approach.
    This is a lightweight version that doesn't require the ADK libraries.

    Args:
        text: Financial text to analyze

    Returns:
        Dict[str, Any]: Sentiment analysis results
    """
    logger.info(f"Analyzing financial sentiment using simple method ({len(text)} chars)")

    # Simple keyword-based sentiment analysis
    positive_keywords = ["growth", "profit", "increase", "positive", "up", "gain", "success"]
    negative_keywords = ["loss", "decline", "decrease", "negative", "down", "risk", "failure"]

    text_lower = text.lower()

    positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
    negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)

    total = positive_count + negative_count
    if total == 0:
        sentiment = "neutral"
        score = 0.5
    else:
        positive_ratio = positive_count / total
        if positive_ratio > 0.6:
            sentiment = "positive"
            score = 0.5 + (positive_ratio - 0.5)
        elif positive_ratio < 0.4:
            sentiment = "negative"
            score = 0.5 - (0.5 - positive_ratio)
        else:
            sentiment = "neutral"
            score = 0.5

    return {
        "sentiment": sentiment,
        "score": score,
        "confidence": 0.7  # Placeholder confidence score
    }

def get_cached_response(query: str) -> Optional[Dict[str, Any]]:
    """
    Get a cached response for a query.

    Args:
        query: The query to look up

    Returns:
        Optional[Dict[str, Any]]: Cached response or None if not found
    """
    # Simple cache lookup
    query_key = query.lower().strip()
    return response_cache.get(query_key)

def cache_response(query: str, response: Dict[str, Any], max_cache_size: int = 100) -> None:
    """
    Cache a response for a query.

    Args:
        query: The query to cache
        response: The response to cache
        max_cache_size: Maximum cache size
    """
    # Simple cache storage with size limit
    query_key = query.lower().strip()
    response_cache[query_key] = response

    # Trim cache if it gets too large
    if len(response_cache) > max_cache_size:
        # Remove oldest entries (this is a simple approach)
        keys_to_remove = list(response_cache.keys())[:-max_cache_size]
        for key in keys_to_remove:
            del response_cache[key]
