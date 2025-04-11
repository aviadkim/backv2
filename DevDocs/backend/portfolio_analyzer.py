import os
import logging
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import math

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PortfolioAnalyzer:
    """Analyze investment portfolios and calculate key metrics."""
    
    def __init__(self, db_connection=None):
        """Initialize the portfolio analyzer."""
        self.db = db_connection
        
        # Default risk-free rate for calculations (e.g., 10-year Treasury yield)
        self.risk_free_rate = 0.035  # 3.5%
        
        # Default market return for calculations (e.g., S&P 500 average)
        self.market_return = 0.10  # 10%
        
        # Default market volatility
        self.market_volatility = 0.15  # 15%
    
    def analyze_portfolio(self, portfolio_data: List[Dict[str, Any]], 
                          historical_data: Optional[Dict[str, List[Dict[str, Any]]]] = None) -> Dict[str, Any]:
        """
        Analyze a portfolio and calculate key metrics.
        
        Args:
            portfolio_data: List of portfolio holdings with details
            historical_data: Optional historical price data for performance and risk calculations
            
        Returns:
            Dictionary with portfolio analysis results
        """
        # Validate input data
        if not portfolio_data:
            return {"error": "No portfolio data provided"}
        
        try:
            # Calculate summary statistics
            summary = self._calculate_summary(portfolio_data)
            
            # Calculate asset allocation
            allocation = self._calculate_allocation(portfolio_data)
            
            # Calculate performance metrics if historical data is available
            performance = {}
            if historical_data:
                performance = self._calculate_performance(portfolio_data, historical_data)
            
            # Calculate risk metrics if historical data is available
            risk = {}
            if historical_data:
                risk = self._calculate_risk_metrics(portfolio_data, historical_data)
            else:
                # Calculate basic risk metrics without historical data
                risk = self._calculate_basic_risk_metrics(portfolio_data)
            
            # Combine all analysis results
            result = {
                "summary": summary,
                "allocation": allocation,
                "performance": performance,
                "risk": risk,
                "analyzed_at": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing portfolio: {str(e)}", exc_info=True)
            return {"error": f"Portfolio analysis failed: {str(e)}"}
    
    def _calculate_summary(self, portfolio_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate portfolio summary statistics."""
        # Initialize summary values
        total_value = 0
        total_cost = 0
        total_gain_loss = 0
        securities_count = len(portfolio_data)
        
        # Process each security
        for item in portfolio_data:
            # Extract value and cost
            value = self._extract_numeric_value(item.get("value", 0))
            cost = self._extract_numeric_value(item.get("cost", item.get("book_value", value)))
            
            # Add to totals
            total_value += value
            total_cost += cost
            total_gain_loss += (value - cost)
        
        # Calculate gain/loss percentage
        gain_loss_percent = (total_gain_loss / total_cost * 100) if total_cost else 0
        
        # Create summary dictionary
        summary = {
            "total_value": total_value,
            "total_cost": total_cost,
            "total_gain_loss": total_gain_loss,
            "total_gain_loss_percent": gain_loss_percent,
            "securities_count": securities_count
        }
        
        return summary
    
    def _calculate_allocation(self, portfolio_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate asset allocation by different dimensions."""
        # Initialize allocation dictionaries
        asset_classes = {}
        sectors = {}
        regions = {}
        currencies = {}
        
        # Calculate total portfolio value
        total_value = sum(self._extract_numeric_value(item.get("value", 0)) for item in portfolio_data)
        
        # Process each security
        for item in portfolio_data:
            value = self._extract_numeric_value(item.get("value", 0))
            
            # Skip items with no value
            if value <= 0:
                continue
            
            # Asset class allocation
            asset_class = item.get("asset_class", "Unknown")
            asset_classes[asset_class] = asset_classes.get(asset_class, 0) + value
            
            # Sector allocation
            sector = item.get("sector", "Unknown")
            sectors[sector] = sectors.get(sector, 0) + value
            
            # Region allocation
            region = item.get("region", "Unknown")
            regions[region] = regions.get(region, 0) + value
            
            # Currency allocation
            currency = item.get("currency", "Unknown")
            currencies[currency] = currencies.get(currency, 0) + value
        
        # Calculate percentages for each allocation dimension
        allocation = {
            "by_asset_class": self._calculate_percentages(asset_classes, total_value),
            "by_sector": self._calculate_percentages(sectors, total_value),
            "by_region": self._calculate_percentages(regions, total_value),
            "by_currency": self._calculate_percentages(currencies, total_value)
        }
        
        return allocation
    
    def _calculate_percentages(self, data_dict: Dict[str, float], total: float) -> Dict[str, Dict[str, float]]:
        """Calculate values and percentages for allocation data."""
        result = {}
        
        if total <= 0:
            return result
        
        for key, value in data_dict.items():
            percent = (value / total * 100) if total else 0
            result[key] = {
                "value": value,
                "percent": percent
            }
        
        return result
    
    def _calculate_performance(self, portfolio_data: List[Dict[str, Any]], 
                              historical_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Calculate performance metrics using historical data."""
        # Initialize performance metrics
        performance = {
            "returns": {
                "1m": 0,
                "3m": 0,
                "6m": 0,
                "ytd": 0,
                "1y": 0,
                "3y": 0,
                "5y": 0,
                "max": 0
            },
            "annualized_returns": {
                "3y": 0,
                "5y": 0,
                "10y": 0
            }
        }
        
        # Calculate total portfolio value
        total_value = sum(self._extract_numeric_value(item.get("value", 0)) for item in portfolio_data)
        
        if total_value <= 0:
            return performance
        
        # Calculate weighted returns for each time period
        for item in portfolio_data:
            value = self._extract_numeric_value(item.get("value", 0))
            weight = value / total_value if total_value > 0 else 0
            
            # Skip items with no value
            if value <= 0:
                continue
            
            # Get identifier (ISIN or ticker)
            identifier = item.get("isin", item.get("ticker", ""))
            
            # Skip if no identifier or no historical data
            if not identifier or identifier not in historical_data:
                continue
            
            # Get historical prices
            prices = historical_data[identifier]
            
            # Calculate returns for different time periods
            returns = self._calculate_security_returns(prices)
            
            # Add weighted returns to portfolio returns
            for period in performance["returns"]:
                if period in returns:
                    performance["returns"][period] += returns[period] * weight
            
            # Add weighted annualized returns
            for period in performance["annualized_returns"]:
                if period in returns:
                    performance["annualized_returns"][period] += returns[period] * weight
        
        return performance
    
    def _calculate_security_returns(self, prices: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate returns for a security over different time periods."""
        # Sort prices by date
        sorted_prices = sorted(prices, key=lambda x: x.get("date", ""))
        
        if not sorted_prices:
            return {}
        
        # Get current price and date
        current_price = sorted_prices[-1].get("price", 0)
        current_date = datetime.fromisoformat(sorted_prices[-1].get("date", datetime.now().isoformat()))
        
        # Initialize returns
        returns = {}
        
        # Define time periods
        periods = {
            "1m": timedelta(days=30),
            "3m": timedelta(days=90),
            "6m": timedelta(days=180),
            "1y": timedelta(days=365),
            "3y": timedelta(days=365 * 3),
            "5y": timedelta(days=365 * 5),
        }
        
        # Calculate returns for each period
        for period, delta in periods.items():
            target_date = current_date - delta
            
            # Find closest price to target date
            closest_price = self._find_closest_price(sorted_prices, target_date)
            
            if closest_price > 0:
                # Calculate return
                period_return = (current_price - closest_price) / closest_price
                returns[period] = period_return
        
        # Calculate YTD return
        ytd_date = datetime(current_date.year, 1, 1)
        ytd_price = self._find_closest_price(sorted_prices, ytd_date)
        
        if ytd_price > 0:
            returns["ytd"] = (current_price - ytd_price) / ytd_price
        
        # Calculate max return (from earliest available price)
        earliest_price = sorted_prices[0].get("price", 0)
        
        if earliest_price > 0:
            returns["max"] = (current_price - earliest_price) / earliest_price
        
        # Calculate annualized returns
        if "3y" in returns:
            returns["3y_annualized"] = (1 + returns["3y"]) ** (1/3) - 1
        
        if "5y" in returns:
            returns["5y_annualized"] = (1 + returns["5y"]) ** (1/5) - 1
        
        # Calculate 10-year return if data is available
        ten_year_date = current_date - timedelta(days=365 * 10)
        ten_year_price = self._find_closest_price(sorted_prices, ten_year_date)
        
        if ten_year_price > 0:
            ten_year_return = (current_price - ten_year_price) / ten_year_price
            returns["10y"] = ten_year_return
            returns["10y_annualized"] = (1 + ten_year_return) ** (1/10) - 1
        
        return returns
    
    def _find_closest_price(self, prices: List[Dict[str, Any]], target_date: datetime) -> float:
        """Find the price closest to the target date."""
        closest_price = 0
        min_delta = timedelta(days=365 * 100)  # Large initial value
        
        for price_data in prices:
            price_date = datetime.fromisoformat(price_data.get("date", ""))
            delta = abs(price_date - target_date)
            
            if delta < min_delta:
                min_delta = delta
                closest_price = price_data.get("price", 0)
        
        return closest_price
    
    def _calculate_risk_metrics(self, portfolio_data: List[Dict[str, Any]], 
                               historical_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Calculate comprehensive risk metrics using historical data."""
        # Initialize risk metrics
        risk = {
            "volatility": 0,
            "sharpe_ratio": 0,
            "sortino_ratio": 0,
            "max_drawdown": 0,
            "beta": 0,
            "alpha": 0,
            "r_squared": 0,
            "var_95": 0,  # Value at Risk (95% confidence)
            "var_99": 0,  # Value at Risk (99% confidence)
            "downside_deviation": 0
        }
        
        # Calculate total portfolio value
        total_value = sum(self._extract_numeric_value(item.get("value", 0)) for item in portfolio_data)
        
        if total_value <= 0:
            return risk
        
        # Prepare data for portfolio return calculation
        portfolio_returns = []
        market_returns = []
        
        # Get market returns if available
        market_data = historical_data.get("MARKET", [])
        
        # Calculate weighted daily returns
        dates = set()
        security_returns = {}
        
        # First, collect all dates and calculate returns for each security
        for item in portfolio_data:
            identifier = item.get("isin", item.get("ticker", ""))
            
            if not identifier or identifier not in historical_data:
                continue
            
            prices = historical_data[identifier]
            
            # Calculate daily returns
            daily_returns = self._calculate_daily_returns(prices)
            security_returns[identifier] = daily_returns
            
            # Collect all dates
            dates.update(daily_returns.keys())
        
        # Sort dates
        sorted_dates = sorted(dates)
        
        # Calculate portfolio returns for each date
        for date in sorted_dates:
            # Calculate weighted return for this date
            portfolio_return = 0
            
            for item in portfolio_data:
                identifier = item.get("isin", item.get("ticker", ""))
                
                if not identifier or identifier not in security_returns:
                    continue
                
                value = self._extract_numeric_value(item.get("value", 0))
                weight = value / total_value if total_value > 0 else 0
                
                if date in security_returns[identifier]:
                    portfolio_return += security_returns[identifier][date] * weight
            
            portfolio_returns.append(portfolio_return)
            
            # Get market return for this date if available
            market_return = 0
            for price_data in market_data:
                if price_data.get("date", "") == date:
                    market_return = price_data.get("return", 0)
                    break
            
            market_returns.append(market_return)
        
        # Calculate risk metrics
        if portfolio_returns:
            # Convert to numpy arrays for calculations
            portfolio_returns_array = np.array(portfolio_returns)
            
            # Calculate volatility (annualized standard deviation)
            volatility = np.std(portfolio_returns_array) * np.sqrt(252)  # Annualize daily volatility
            risk["volatility"] = volatility
            
            # Calculate average return (annualized)
            avg_return = np.mean(portfolio_returns_array) * 252  # Annualize daily return
            
            # Calculate Sharpe ratio
            risk["sharpe_ratio"] = (avg_return - self.risk_free_rate) / volatility if volatility > 0 else 0
            
            # Calculate Sortino ratio (using downside deviation)
            negative_returns = portfolio_returns_array[portfolio_returns_array < 0]
            downside_deviation = np.std(negative_returns) * np.sqrt(252) if len(negative_returns) > 0 else 0
            risk["downside_deviation"] = downside_deviation
            risk["sortino_ratio"] = (avg_return - self.risk_free_rate) / downside_deviation if downside_deviation > 0 else 0
            
            # Calculate maximum drawdown
            cumulative_returns = np.cumprod(1 + portfolio_returns_array)
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdowns = (cumulative_returns - running_max) / running_max
            risk["max_drawdown"] = abs(np.min(drawdowns)) if len(drawdowns) > 0 else 0
            
            # Calculate Value at Risk (VaR)
            risk["var_95"] = np.percentile(portfolio_returns_array, 5) * total_value  # 95% VaR
            risk["var_99"] = np.percentile(portfolio_returns_array, 1) * total_value  # 99% VaR
            
            # Calculate Beta and Alpha if market data is available
            if market_returns and len(market_returns) == len(portfolio_returns):
                market_returns_array = np.array(market_returns)
                
                # Calculate covariance and market variance
                covariance = np.cov(portfolio_returns_array, market_returns_array)[0, 1]
                market_variance = np.var(market_returns_array)
                
                # Calculate beta
                beta = covariance / market_variance if market_variance > 0 else 1
                risk["beta"] = beta
                
                # Calculate alpha (annualized)
                market_avg_return = np.mean(market_returns_array) * 252
                alpha = avg_return - (self.risk_free_rate + beta * (market_avg_return - self.risk_free_rate))
                risk["alpha"] = alpha
                
                # Calculate R-squared
                correlation = np.corrcoef(portfolio_returns_array, market_returns_array)[0, 1]
                risk["r_squared"] = correlation ** 2
        
        return risk
    
    def _calculate_basic_risk_metrics(self, portfolio_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate basic risk metrics without historical data."""
        # Initialize risk metrics
        risk = {
            "concentration_risk": 0,
            "currency_risk": 0,
            "liquidity_risk": 0,
            "diversification_score": 0
        }
        
        # Calculate total portfolio value
        total_value = sum(self._extract_numeric_value(item.get("value", 0)) for item in portfolio_data)
        
        if total_value <= 0:
            return risk
        
        # Calculate concentration risk (Herfindahl-Hirschman Index)
        hhi = sum((self._extract_numeric_value(item.get("value", 0)) / total_value) ** 2 for item in portfolio_data)
        risk["concentration_risk"] = hhi
        
        # Calculate diversification score (inverse of HHI, normalized)
        risk["diversification_score"] = (1 - hhi) * 100
        
        # Calculate currency risk (percentage in non-base currencies)
        base_currency = self._identify_base_currency(portfolio_data)
        foreign_currency_value = sum(
            self._extract_numeric_value(item.get("value", 0)) 
            for item in portfolio_data 
            if item.get("currency", base_currency) != base_currency
        )
        risk["currency_risk"] = (foreign_currency_value / total_value) * 100 if total_value > 0 else 0
        
        # Calculate liquidity risk (percentage in illiquid assets)
        illiquid_asset_classes = ["Private Equity", "Real Estate", "Hedge Fund", "Venture Capital", "Private Debt"]
        illiquid_value = sum(
            self._extract_numeric_value(item.get("value", 0)) 
            for item in portfolio_data 
            if item.get("asset_class", "") in illiquid_asset_classes
        )
        risk["liquidity_risk"] = (illiquid_value / total_value) * 100 if total_value > 0 else 0
        
        return risk
    
    def _calculate_daily_returns(self, prices: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate daily returns from price data."""
        # Sort prices by date
        sorted_prices = sorted(prices, key=lambda x: x.get("date", ""))
        
        # Calculate daily returns
        daily_returns = {}
        
        for i in range(1, len(sorted_prices)):
            current_price = sorted_prices[i].get("price", 0)
            previous_price = sorted_prices[i-1].get("price", 0)
            date = sorted_prices[i].get("date", "")
            
            if previous_price > 0 and date:
                daily_return = (current_price - previous_price) / previous_price
                daily_returns[date] = daily_return
        
        return daily_returns
    
    def _identify_base_currency(self, portfolio_data: List[Dict[str, Any]]) -> str:
        """Identify the base currency of the portfolio (most common currency)."""
        currency_counts = {}
        
        for item in portfolio_data:
            currency = item.get("currency", "Unknown")
            currency_counts[currency] = currency_counts.get(currency, 0) + 1
        
        # Find the most common currency
        base_currency = max(currency_counts.items(), key=lambda x: x[1])[0] if currency_counts else "USD"
        
        return base_currency
    
    def _extract_numeric_value(self, value: Any) -> float:
        """Extract numeric value from various formats."""
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Remove currency symbols and commas
            cleaned_value = value.replace('$', '').replace('€', '').replace('£', '').replace('¥', '').replace(',', '')
            
            # Handle percentage values
            if '%' in cleaned_value:
                cleaned_value = cleaned_value.replace('%', '')
                try:
                    return float(cleaned_value) / 100
                except ValueError:
                    return 0
            
            # Handle K, M, B suffixes
            if 'K' in cleaned_value or 'k' in cleaned_value:
                cleaned_value = cleaned_value.replace('K', '').replace('k', '')
                try:
                    return float(cleaned_value) * 1000
                except ValueError:
                    return 0
            
            if 'M' in cleaned_value or 'm' in cleaned_value:
                cleaned_value = cleaned_value.replace('M', '').replace('m', '')
                try:
                    return float(cleaned_value) * 1000000
                except ValueError:
                    return 0
            
            if 'B' in cleaned_value or 'b' in cleaned_value:
                cleaned_value = cleaned_value.replace('B', '').replace('b', '')
                try:
                    return float(cleaned_value) * 1000000000
                except ValueError:
                    return 0
            
            # Try to convert to float
            try:
                return float(cleaned_value)
            except ValueError:
                return 0
        
        return 0
    
    def generate_portfolio_recommendations(self, portfolio_data: List[Dict[str, Any]], 
                                          risk_profile: str = "moderate") -> Dict[str, Any]:
        """Generate investment recommendations based on portfolio analysis."""
        # Analyze the portfolio
        analysis = self.analyze_portfolio(portfolio_data)
        
        # Initialize recommendations
        recommendations = {
            "summary": "",
            "allocation_recommendations": [],
            "security_recommendations": [],
            "risk_recommendations": []
        }
        
        # Define target allocations based on risk profile
        target_allocations = {
            "conservative": {
                "Equity": 30,
                "Fixed Income": 50,
                "Cash": 15,
                "Alternative": 5
            },
            "moderate": {
                "Equity": 50,
                "Fixed Income": 35,
                "Cash": 5,
                "Alternative": 10
            },
            "aggressive": {
                "Equity": 70,
                "Fixed Income": 20,
                "Cash": 0,
                "Alternative": 10
            }
        }
        
        # Get current allocations
        current_allocations = {}
        if "allocation" in analysis and "by_asset_class" in analysis["allocation"]:
            for asset_class, data in analysis["allocation"]["by_asset_class"].items():
                current_allocations[asset_class] = data.get("percent", 0)
        
        # Map custom asset classes to standard ones
        asset_class_mapping = {
            "Stock": "Equity",
            "Stocks": "Equity",
            "Shares": "Equity",
            "Bond": "Fixed Income",
            "Bonds": "Fixed Income",
            "ETF": "Equity",  # Simplified mapping
            "Mutual Fund": "Equity",  # Simplified mapping
            "Cash Equivalent": "Cash",
            "Money Market": "Cash",
            "Real Estate": "Alternative",
            "Commodity": "Alternative",
            "Hedge Fund": "Alternative",
            "Private Equity": "Alternative",
            "Venture Capital": "Alternative",
            "Cryptocurrency": "Alternative"
        }
        
        # Standardize current allocations
        standardized_allocations = {}
        for asset_class, percent in current_allocations.items():
            standard_class = asset_class_mapping.get(asset_class, asset_class)
            standardized_allocations[standard_class] = standardized_allocations.get(standard_class, 0) + percent
        
        # Get target allocation for the given risk profile
        profile_targets = target_allocations.get(risk_profile, target_allocations["moderate"])
        
        # Generate allocation recommendations
        for asset_class, target_percent in profile_targets.items():
            current_percent = standardized_allocations.get(asset_class, 0)
            difference = target_percent - current_percent
            
            if abs(difference) >= 5:  # Only recommend changes of 5% or more
                direction = "increase" if difference > 0 else "decrease"
                recommendations["allocation_recommendations"].append({
                    "asset_class": asset_class,
                    "current_allocation": current_percent,
                    "target_allocation": target_percent,
                    "difference": abs(difference),
                    "recommendation": f"{direction.capitalize()} {asset_class} allocation by {abs(difference):.1f}%"
                })
        
        # Generate risk recommendations
        if "risk" in analysis:
            risk_metrics = analysis["risk"]
            
            # Check diversification
            if "diversification_score" in risk_metrics and risk_metrics["diversification_score"] < 70:
                recommendations["risk_recommendations"].append({
                    "type": "diversification",
                    "severity": "high" if risk_metrics["diversification_score"] < 50 else "medium",
                    "recommendation": "Increase portfolio diversification by adding more securities across different sectors and asset classes."
                })
            
            # Check concentration risk
            if "concentration_risk" in risk_metrics and risk_metrics["concentration_risk"] > 0.2:
                recommendations["risk_recommendations"].append({
                    "type": "concentration",
                    "severity": "high" if risk_metrics["concentration_risk"] > 0.3 else "medium",
                    "recommendation": "Reduce concentration risk by decreasing exposure to the largest positions."
                })
            
            # Check currency risk
            if "currency_risk" in risk_metrics and risk_metrics["currency_risk"] > 30:
                recommendations["risk_recommendations"].append({
                    "type": "currency",
                    "severity": "medium",
                    "recommendation": "Consider hedging currency risk or reducing exposure to foreign currencies."
                })
            
            # Check liquidity risk
            if "liquidity_risk" in risk_metrics and risk_metrics["liquidity_risk"] > 20:
                recommendations["risk_recommendations"].append({
                    "type": "liquidity",
                    "severity": "medium",
                    "recommendation": "Increase allocation to more liquid assets to improve portfolio liquidity."
                })
        
        # Generate security-specific recommendations
        for item in portfolio_data:
            value = self._extract_numeric_value(item.get("value", 0))
            total_value = analysis["summary"].get("total_value", 0)
            
            # Check for overweight positions
            if total_value > 0 and value / total_value > 0.1:  # Position > 10% of portfolio
                recommendations["security_recommendations"].append({
                    "security": item.get("security", "Unknown"),
                    "isin": item.get("isin", ""),
                    "type": "overweight",
                    "recommendation": f"Consider reducing position in {item.get('security', 'this security')} to decrease concentration risk."
                })
        
        # Generate summary recommendation
        if recommendations["allocation_recommendations"] or recommendations["risk_recommendations"]:
            summary = "Based on your portfolio analysis and risk profile, we recommend: "
            
            if recommendations["allocation_recommendations"]:
                allocation_changes = [rec["recommendation"] for rec in recommendations["allocation_recommendations"][:2]]
                summary += ", ".join(allocation_changes)
                
                if recommendations["risk_recommendations"]:
                    summary += "; "
            
            if recommendations["risk_recommendations"]:
                risk_changes = [rec["recommendation"] for rec in recommendations["risk_recommendations"][:2]]
                summary += ", ".join(risk_changes)
            
            recommendations["summary"] = summary
        else:
            recommendations["summary"] = "Your portfolio is well-aligned with your risk profile. No major changes recommended at this time."
        
        return recommendations
