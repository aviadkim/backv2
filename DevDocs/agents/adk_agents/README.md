# ADK Agents (Lightweight Implementation)

This directory contains lightweight agent implementations inspired by Google's Agent Development Kit (ADK). This implementation is optimized for low resource usage while still providing the core functionality needed for financial document processing.

## Overview

The Agent Development Kit (ADK) is an open-source framework by Google designed to facilitate the creation and deployment of AI agents, particularly those powered by large language models (LLMs) like Google's Gemini. This lightweight implementation provides a similar interface without the heavy resource requirements.

## Agents

### FinancialAgent (Lightweight)

The `FinancialAgent` is designed to process financial documents, extract key data points, and provide financial insights. It simulates ADK's capabilities with minimal resource usage:

- Extract financial metrics from document text using simple pattern matching
- Analyze financial sentiment using keyword-based approaches
- Provide basic insights based on financial data
- Implement caching to reduce redundant processing
- Use lazy loading to minimize memory footprint

## Resource Optimization Features

1. **Lazy Loading**: Components are only initialized when needed
2. **Response Caching**: Frequently requested information is cached to avoid reprocessing
3. **Minimal Dependencies**: Reduced external library requirements
4. **Low Resource Mode**: Simplified processing for resource-constrained environments

## Setup

1. No external dependencies required for the lightweight version

2. Run the example script:

```bash
python example.py
```

## Usage

```python
from agents.adk_agents.financial_agent import FinancialAgent

# Create the agent with low resource configuration
agent = FinancialAgent(
    agent_id="unique_id",
    name="Financial Analysis Agent (Lightweight)",
    description="Agent for analyzing financial documents",
    config={
        "low_resource_mode": True,
        "use_cache": True,
        "cache_size": 50
    }
)

# Process a query
response = await agent.process("Analyze this financial document: ...")

# Access the response
print(response.content)
```

## Configuration

The agent can be configured with the following parameters:

- `low_resource_mode`: Whether to use low resource mode (default: True)
- `use_cache`: Whether to cache responses (default: True)
- `cache_size`: Maximum number of cached responses (default: 100)
- `lazy_loading`: Whether to load components lazily (default: True)

## Utility Functions

The agent comes with the following utility functions:

- `extract_financial_data_simple`: Extracts key financial metrics from document text
- `analyze_financial_sentiment_simple`: Analyzes the sentiment of financial text
- `get_cached_response`: Retrieves cached responses
- `cache_response`: Stores responses in the cache

## Future Enhancements

1. **Full ADK Integration**: When resources permit, this lightweight implementation can be upgraded to use the full ADK
2. **Additional Tools**: More specialized financial analysis tools can be added
3. **Improved Extraction**: More sophisticated extraction techniques can be implemented
