# API Documentation

This document provides details on the available API endpoints for the Financial Document Analysis Application.

## Base URL

All API endpoints are relative to the base URL:

```
http://localhost:24125/api
```

## Authentication

Most API endpoints require authentication. Include an `Authorization` header with a valid JWT token:

```
Authorization: Bearer <token>
```

## Endpoints

### Document Processing

#### Process Document

Process a document and extract financial information.

- **URL**: `/document/process`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file`: The document file to process
  - `type` (optional): Document type hint (e.g., `annual_report`, `portfolio_statement`)
  - `processing_options` (optional): JSON string with processing options

**Example Request:**
```bash
curl -X POST \
  http://localhost:24125/api/document/process \
  -H 'Authorization: Bearer <token>' \
  -F 'file=@financial_report.pdf' \
  -F 'type=annual_report'
```

**Example Response:**
```json
{
  "status": "success",
  "message": "File processed successfully",
  "result": {
    "document_id": "123e4567-e89b-12d3-a456-426614174000",
    "file_type": "pdf",
    "file_size": 1234567,
    "text_length": 45678,
    "financial_data": {
      "currencies": ["$", "€"],
      "amounts": ["$1,250,000", "$750,000", "$500,000"],
      "percentages": ["10.5%", "5.2%", "15.8%"],
      "dates": ["2023-01-01", "2023-12-31"]
    },
    "financial_statements": {
      "income_statement": {
        "line_items": [
          {"label": "Revenue", "value": "$1,250,000"},
          {"label": "Cost of Goods Sold", "value": "$750,000"},
          {"label": "Gross Profit", "value": "$500,000"}
        ],
        "period": "2023-01-01 to 2023-12-31",
        "currency": "USD"
      }
    },
    "portfolio_data": [
      {
        "security": "Apple Inc. (AAPL)",
        "isin": "US0378331005",
        "quantity": "100",
        "price": "$175.25",
        "value": "$17,525"
      }
    ]
  }
}
```

### Financial Analysis

#### Analyze Portfolio

Analyze a portfolio and calculate key metrics.

- **URL**: `/financial/analyze-portfolio`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Parameters**:
  - `portfolio`: Array of portfolio holdings
  - `historical_data` (optional): Historical price data for performance calculations

**Example Request:**
```bash
curl -X POST \
  http://localhost:24125/api/financial/analyze-portfolio \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "portfolio": [
      {
        "security": "Apple Inc.",
        "isin": "US0378331005",
        "ticker": "AAPL",
        "asset_class": "Equity",
        "sector": "Technology",
        "quantity": 100,
        "price": 175.25,
        "value": 17525,
        "cost": 15000
      }
    ]
  }'
```

**Example Response:**
```json
{
  "status": "success",
  "result": {
    "summary": {
      "total_value": 17525,
      "total_cost": 15000,
      "total_gain_loss": 2525,
      "total_gain_loss_percent": 16.83,
      "securities_count": 1
    },
    "allocation": {
      "by_asset_class": {
        "Equity": {
          "value": 17525,
          "percent": 100
        }
      },
      "by_sector": {
        "Technology": {
          "value": 17525,
          "percent": 100
        }
      }
    },
    "risk": {
      "concentration_risk": 1,
      "diversification_score": 0
    },
    "analyzed_at": "2023-06-30T12:34:56.789Z"
  }
}
```

#### Generate Report

Generate a financial report.

- **URL**: `/financial/generate-report`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Parameters**:
  - `report_type`: Type of report to generate (e.g., `portfolio`, `profit_loss`, `balance_sheet`)
  - `data`: Data to include in the report
  - `output_format` (optional): Format of the report output (`json`, `html`, `pdf`, `markdown`)

**Example Request:**
```bash
curl -X POST \
  http://localhost:24125/api/financial/generate-report \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "report_type": "portfolio",
    "data": {
      "summary": {
        "total_value": 44687.5,
        "total_cost": 40250,
        "total_gain_loss": 4437.5,
        "total_gain_loss_percent": 11.02,
        "securities_count": 3
      },
      "holdings": [
        {
          "security": "Apple Inc.",
          "isin": "US0378331005",
          "ticker": "AAPL",
          "asset_class": "Equity",
          "sector": "Technology",
          "value": 17525,
          "weight": 39.22,
          "gain_loss": 2525,
          "gain_loss_percent": 16.83
        }
      ]
    },
    "output_format": "json"
  }'
```

**Example Response:**
```json
{
  "status": "success",
  "report": {
    "report_type": "portfolio",
    "generated_at": "2023-06-30T12:34:56.789Z",
    "data": {
      "title": "Portfolio Analysis Report",
      "summary": {
        "total_value": "$44,687.50",
        "total_cost": "$40,250.00",
        "total_gain_loss": "$4,437.50",
        "total_gain_loss_percent": "11.02%",
        "securities_count": 3
      },
      "holdings": [
        {
          "security": "Apple Inc.",
          "isin": "US0378331005",
          "ticker": "AAPL",
          "asset_class": "Equity",
          "sector": "Technology",
          "value": {
            "value": 17525,
            "formatted": "$17,525.00"
          },
          "weight": {
            "value": 39.22,
            "formatted": "39.22%"
          },
          "gain_loss": {
            "value": 2525,
            "formatted": "$2,525.00"
          },
          "gain_loss_percent": {
            "value": 16.83,
            "formatted": "16.83%"
          }
        }
      ]
    }
  }
}
```

### AI Analysis

#### AI Financial Analysis

Analyze financial data with AI.

- **URL**: `/financial/ai-analysis`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Parameters**:
  - `analysis_type`: Type of analysis to perform (e.g., `document`, `portfolio`, `metrics`, `trends`)
  - Additional parameters depending on the analysis type

**Example Request:**
```bash
curl -X POST \
  http://localhost:24125/api/financial/ai-analysis \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "analysis_type": "portfolio",
    "portfolio_data": {
      "summary": {
        "total_value": 44687.5,
        "total_cost": 40250,
        "total_gain_loss": 4437.5,
        "total_gain_loss_percent": 11.02,
        "securities_count": 3
      },
      "allocation": {
        "by_asset_class": {
          "Equity": {
            "value": 33812.5,
            "percent": 75.66
          },
          "Bond": {
            "value": 10875,
            "percent": 24.34
          }
        }
      }
    },
    "risk_profile": "moderate"
  }'
```

**Example Response:**
```json
{
  "status": "success",
  "result": {
    "overall_assessment": "The portfolio is well-diversified with a moderate risk profile...",
    "asset_allocation_recommendations": [
      {
        "asset_class": "Equity",
        "current_allocation": "75.66%",
        "recommended_allocation": "70%",
        "rationale": "Slightly reduce equity exposure to align with moderate risk profile"
      }
    ],
    "investment_recommendations": [
      {
        "action": "buy",
        "security_type": "ETF",
        "description": "International Equity ETF",
        "rationale": "Increase international diversification"
      }
    ],
    "risk_management": [
      {
        "strategy": "Hedging",
        "description": "Consider adding a small allocation to gold or other inflation hedges"
      }
    ],
    "summary": "Overall, the portfolio is performing well but could benefit from increased international diversification and inflation protection."
  }
}
```

## Error Responses

All API endpoints return a standard error format:

```json
{
  "status": "error",
  "error": "Error message describing what went wrong"
}
```

Common HTTP status codes:

- `400 Bad Request`: Invalid input parameters
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

## Rate Limiting

API requests are limited to 100 requests per minute per user. If you exceed this limit, you will receive a `429 Too Many Requests` response.
