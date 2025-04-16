"""
Create top holdings report with comprehensive information.
"""
import json

# Define the top 5 holdings based on the extracted data
top_holdings = [
    {
        "isin": "XS2567543397",
        "description": "GS 10Y CALLABLE NOTE 2024-18.06.2034",
        "nominal": 2450000.0,
        "acquisition_price": 100.1,
        "current_price": 100.59,
        "change_1m": 1.33,
        "change_ytd": 0.49,
        "valuation": 2560667.0,
        "percentage": 13.12,
        "maturity_date": "18.06.2034",
        "coupon": "18.6 // Annual 5.61%",
        "security_type": "Ordinary Bonds",
        "prc": 4.0,
        "ytm": 5.52,
        "currency": "USD"
    },
    {
        "isin": "XS2838389430",
        "description": "LUMINIS 5.7% STR NOTE 2024-26.04.33 WFC 24W",
        "nominal": 1600000.0,
        "acquisition_price": 100.1,
        "current_price": 97.53,
        "change_1m": 0.82,
        "change_ytd": -2.57,
        "valuation": 1623560.0,
        "percentage": 8.32,
        "maturity_date": "26.04.2033",
        "coupon": "Annual 5.7%",
        "security_type": "Structured Bonds",
        "prc": 5.0,
        "ytm": None,
        "currency": "USD"
    },
    {
        "isin": "XS2964611052",
        "description": "DEUTSCHE BANK 0 % NOTES 2025-14.02.35",
        "nominal": 1470000.0,
        "acquisition_price": 100.0,
        "current_price": 101.25,
        "change_1m": 1.25,
        "change_ytd": 1.25,
        "valuation": 1488375.0,
        "percentage": 7.63,
        "maturity_date": "14.02.2035",
        "coupon": None,
        "security_type": "Zero Bonds",
        "prc": 4.0,
        "ytm": 5.31,
        "currency": "USD"
    },
    {
        "isin": "XS2665592833",
        "description": "HARP ISSUER (4% MIN/5,5% MAX) NOTES 2023-18.09.2028",
        "nominal": 1500000.0,
        "acquisition_price": 99.099,
        "current_price": 98.39,
        "change_1m": 1.51,
        "change_ytd": -0.72,
        "valuation": 1502850.0,
        "percentage": 7.70,
        "maturity_date": "18.09.2028",
        "coupon": "18.9 // Annual 4%",
        "security_type": "Ordinary Bonds",
        "prc": 4.0,
        "ytm": None,
        "currency": "USD"
    },
    {
        "isin": "XS2792098779",
        "description": "CITIGROUP",
        "nominal": 1200000.0,
        "acquisition_price": 100.0,
        "current_price": 98.065,
        "change_1m": 0.08,
        "change_ytd": -1.94,
        "valuation": 1176780.0,
        "percentage": 6.03,
        "maturity_date": "02.12.2034",
        "coupon": None,
        "security_type": "Structured Bonds",
        "prc": 5.0,
        "ytm": None,
        "currency": "USD"
    }
]

# Save the top holdings
with open("top_holdings_comprehensive.json", "w", encoding="utf-8") as f:
    json.dump(top_holdings, f, indent=2)

print("Top 5 holdings saved to top_holdings_comprehensive.json")

# Create a more readable report
report = """# Top 5 Holdings in Messos Portfolio

## 1. GS 10Y CALLABLE NOTE (XS2567543397)
- **Description**: GS 10Y CALLABLE NOTE 2024-18.06.2034
- **Type**: Ordinary Bonds
- **Nominal**: $2,450,000.00
- **Acquisition Price**: 100.10
- **Current Price**: 100.59
- **Valuation**: $2,560,667.00 (13.12% of portfolio)
- **Change (1 month)**: +1.33%
- **Change (YTD)**: +0.49%
- **Maturity Date**: June 18, 2034
- **Coupon**: 18.6 (Annual 5.61%)
- **PRC**: 4.00
- **YTM**: 5.52

## 2. LUMINIS STR NOTE (XS2838389430)
- **Description**: LUMINIS 5.7% STR NOTE 2024-26.04.33 WFC 24W
- **Type**: Structured Bonds
- **Nominal**: $1,600,000.00
- **Acquisition Price**: 100.10
- **Current Price**: 97.53
- **Valuation**: $1,623,560.00 (8.32% of portfolio)
- **Change (1 month)**: +0.82%
- **Change (YTD)**: -2.57%
- **Maturity Date**: April 26, 2033
- **Coupon**: Annual 5.7%
- **PRC**: 5.00

## 3. DEUTSCHE BANK NOTES (XS2964611052)
- **Description**: DEUTSCHE BANK 0% NOTES 2025-14.02.35
- **Type**: Zero Bonds
- **Nominal**: $1,470,000.00
- **Acquisition Price**: 100.00
- **Current Price**: 101.25
- **Valuation**: $1,488,375.00 (7.63% of portfolio)
- **Change (1 month)**: +1.25%
- **Change (YTD)**: +1.25%
- **Maturity Date**: February 14, 2035
- **PRC**: 4.00
- **YTM**: 5.31

## 4. HARP ISSUER NOTES (XS2665592833)
- **Description**: HARP ISSUER (4% MIN/5,5% MAX) NOTES 2023-18.09.2028
- **Type**: Ordinary Bonds
- **Nominal**: $1,500,000.00
- **Acquisition Price**: 99.10
- **Current Price**: 98.39
- **Valuation**: $1,502,850.00 (7.70% of portfolio)
- **Change (1 month)**: +1.51%
- **Change (YTD)**: -0.72%
- **Maturity Date**: September 18, 2028
- **Coupon**: 18.9 (Annual 4%)
- **PRC**: 4.00

## 5. CITIGROUP (XS2792098779)
- **Description**: CITIGROUP
- **Type**: Structured Bonds
- **Nominal**: $1,200,000.00
- **Acquisition Price**: 100.00
- **Current Price**: 98.07
- **Valuation**: $1,176,780.00 (6.03% of portfolio)
- **Change (1 month)**: +0.08%
- **Change (YTD)**: -1.94%
- **Maturity Date**: December 2, 2034
- **PRC**: 5.00

## Summary
These top 5 holdings represent $8,352,232.00, which is 42.80% of the total portfolio value of $19,510,599.00. The portfolio has a diverse mix of structured bonds, zero bonds, and ordinary bonds with varying maturities and risk profiles.
"""

# Save the report
with open("top_holdings_report.md", "w", encoding="utf-8") as f:
    f.write(report)

print("Top holdings report saved to top_holdings_report.md")
