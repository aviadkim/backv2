"""
Financial Advisor Agent for advanced financial analysis and recommendations.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import re
import uuid
from .base_agent import BaseAgent

class FinancialAdvisorAgent(BaseAgent):
    """Agent for financial analysis, accounting, and investment advice."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the financial advisor agent.

        Args:
            api_key: OpenRouter API key
            **kwargs: Additional parameters for the base agent
        """
        super().__init__(name="Financial Advisor Agent")
        self.api_key = api_key
        self.description = "I provide financial analysis, accounting, and investment advice."

        # Asset class classification dictionary
        self.asset_classes = {
            "stocks": ["מניות", "stocks", "equities", "מניה", "stock"],
            "bonds": ["אג\"ח", "אגח", "אגרות חוב", "bonds", "bond", "fixed income"],
            "cash": ["מזומן", "פקדון", "פקדונות", "עו\"ש", "cash", "deposit", "deposits"],
            "etf": ["תעודות סל", "קרנות סל", "etf", "exchange traded fund"],
            "funds": ["קרן", "קרנות", "fund", "funds", "mutual fund"],
            "real_estate": ["נדל\"ן", "נדלן", "real estate", "reit"],
            "commodities": ["סחורות", "זהב", "כסף", "נפט", "commodities", "gold", "silver", "oil"],
            "alternatives": ["השקעות אלטרנטיביות", "גידור", "alternatives", "hedge", "private equity"]
        }

        # Industry sector classification dictionary
        self.industry_sectors = {
            "technology": ["טכנולוגיה", "מחשבים", "תוכנה", "technology", "software", "computers"],
            "healthcare": ["בריאות", "רפואה", "תרופות", "healthcare", "medical", "pharma"],
            "finance": ["פיננסים", "בנקאות", "ביטוח", "finance", "banking", "insurance"],
            "consumer": ["צריכה", "קמעונאות", "מזון", "consumer", "retail", "food"],
            "energy": ["אנרגיה", "נפט", "גז", "energy", "oil", "gas"],
            "materials": ["חומרי גלם", "כימיקלים", "מתכות", "materials", "chemicals", "metals"],
            "utilities": ["תשתיות", "חשמל", "מים", "utilities", "electricity", "water"],
            "telecom": ["תקשורת", "מדיה", "telecom", "media"],
            "industrial": ["תעשייה", "ייצור", "industrial", "manufacturing"]
        }

        # Risk thresholds
        self.risk_thresholds = {
            "low": {
                "volatility": 10.0,  # Annual volatility
                "max_single_holding": 5.0,  # Maximum percentage of portfolio in a single asset
                "min_investment_grade": 70.0  # Minimum percentage of investment grade bonds
            },
            "medium": {
                "volatility": 15.0,
                "max_single_holding": 10.0,
                "min_investment_grade": 50.0
            },
            "high": {
                "volatility": 25.0,
                "max_single_holding": 20.0,
                "min_investment_grade": 30.0
            }
        }

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task to provide financial advice.

        Args:
            task: Task dictionary with the following keys:
                - analysis_type: Type of analysis to perform (portfolio, financial_statements, salary, investment_suggestion)
                - document_data: Document data to analyze
                - risk_profile: Optional risk profile for portfolio analysis (low, medium, high)
                - investment_amount: Optional investment amount for investment suggestions

        Returns:
            Dictionary with analysis results
        """
        # Get the required data
        analysis_type = task.get('analysis_type', 'portfolio')
        document_data = task.get('document_data', {})
        risk_profile = task.get('risk_profile', 'medium')
        investment_amount = task.get('investment_amount', 0)

        # Check if we have document data to analyze
        if not document_data:
            return {
                'status': 'error',
                'message': 'No document data provided for analysis'
            }

        # Perform the analysis based on type
        try:
            if analysis_type == 'portfolio':
                result = self.analyze_portfolio(document_data, risk_profile)
            elif analysis_type == 'financial_statements':
                result = self.analyze_financial_statements(document_data)
            elif analysis_type == 'salary':
                result = self.analyze_salary(document_data)
            elif analysis_type == 'investment_suggestion':
                result = self.generate_investment_suggestion(document_data, investment_amount, risk_profile)
            else:
                return {
                    'status': 'error',
                    'message': f'Unsupported analysis type: {analysis_type}'
                }

            # Add analysis ID and timestamp
            result['analysis_id'] = str(uuid.uuid4())
            if 'analysis_date' not in result:
                result['analysis_date'] = datetime.now().isoformat()

            return result
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error performing financial analysis: {str(e)}'
            }

    def analyze_portfolio(self, document_data: Dict[str, Any], risk_profile: str = "medium") -> Dict[str, Any]:
        """
        Analyze a portfolio and provide recommendations.

        Args:
            document_data: Processed document data
            risk_profile: Desired risk profile (low / medium / high)

        Returns:
            Dictionary with analysis and recommendations
        """
        # Validate risk profile
        if risk_profile not in self.risk_thresholds:
            risk_profile = "medium"

        # Extract portfolio data
        portfolio_data = self._extract_portfolio_data(document_data)
        if not portfolio_data:
            return {
                "status": "error",
                "message": "No portfolio data found in the document"
            }

        # Basic portfolio analysis
        basic_analysis = self._analyze_basic_portfolio(portfolio_data)

        # Asset allocation analysis
        asset_allocation = self._analyze_asset_allocation(portfolio_data)

        # Performance analysis
        performance_analysis = self._analyze_performance(portfolio_data)

        # Risk analysis
        risk_analysis = self._analyze_risk(portfolio_data, risk_profile)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            basic_analysis,
            asset_allocation,
            performance_analysis,
            risk_analysis,
            risk_profile
        )

        return {
            "status": "success",
            "analysis_date": datetime.now().isoformat(),
            "basic_analysis": basic_analysis,
            "asset_allocation": asset_allocation,
            "performance": performance_analysis,
            "risk_analysis": risk_analysis,
            "recommendations": recommendations
        }

    def _extract_portfolio_data(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract portfolio data from a document."""
        portfolio_data = {}

        # Look in financial data
        if "financial_data" in document_data and "portfolio" in document_data["financial_data"]:
            portfolio = document_data["financial_data"]["portfolio"]

            # Summary
            if "summary" in portfolio:
                portfolio_data.update(portfolio["summary"])

            # Securities list
            if "securities" in portfolio:
                portfolio_data["securities"] = portfolio["securities"]

                # Calculate summaries
                if "securities" in portfolio_data:
                    securities = portfolio_data["securities"]
                    total_value = sum(sec.get("value", 0) for sec in securities
                                   if isinstance(sec.get("value", 0), (int, float)))

                    portfolio_data["total_value"] = total_value

        # If no portfolio info found, look in general summary
        elif "summary" in document_data and "total_portfolio_value" in document_data["summary"]:
            portfolio_data["total_value"] = document_data["summary"]["total_portfolio_value"]

        # Look in tables
        elif "tables" in document_data:
            for table in document_data["tables"]:
                if table.get("type") == "portfolio" and "data" in table:
                    # Create securities list from table
                    securities = []

                    for row in table["data"]:
                        security = {}

                        # Look for common fields
                        for key, value in row.items():
                            key_lower = str(key).lower()

                            # Security name
                            if "name" in key_lower or "description" in key_lower:
                                security["name"] = value
                            # ISIN
                            elif "isin" in key_lower:
                                security["isin"] = value
                            # Security type
                            elif "type" in key_lower:
                                security["type"] = value
                            # Quantity
                            elif "quantity" in key_lower or "amount" in key_lower:
                                security["quantity"] = self._parse_numeric(value)
                            # Price
                            elif "price" in key_lower or "rate" in key_lower:
                                security["price"] = self._parse_numeric(value)
                            # Value
                            elif "value" in key_lower or "total" in key_lower:
                                security["value"] = self._parse_numeric(value)
                            # Return
                            elif "return" in key_lower or "yield" in key_lower:
                                security["return"] = self._parse_numeric(value)

                        if security:
                            securities.append(security)

                    if securities:
                        portfolio_data["securities"] = securities

                        # Calculate summaries
                        total_value = sum(sec.get("value", 0) for sec in securities
                                       if isinstance(sec.get("value", 0), (int, float)))

                        portfolio_data["total_value"] = total_value

                        break

        return portfolio_data

    def _analyze_basic_portfolio(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Basic portfolio analysis."""
        basic_analysis = {
            "total_value": portfolio_data.get("total_value", 0),
            "security_count": 0,
            "average_security_value": 0,
            "largest_holdings": [],
            "asset_types": {}
        }

        if "securities" in portfolio_data:
            securities = portfolio_data["securities"]
            basic_analysis["security_count"] = len(securities)

            if securities and basic_analysis["total_value"] > 0:
                basic_analysis["average_security_value"] = basic_analysis["total_value"] / len(securities)

                # Find largest holdings
                sorted_securities = sorted(
                    [sec for sec in securities if isinstance(sec.get("value", 0), (int, float))],
                    key=lambda x: x.get("value", 0),
                    reverse=True
                )

                basic_analysis["largest_holdings"] = sorted_securities[:5]

                # Classify by asset type
                for security in securities:
                    asset_type = self._classify_asset_type(security)

                    if asset_type not in basic_analysis["asset_types"]:
                        basic_analysis["asset_types"][asset_type] = {
                            "count": 0,
                            "total_value": 0,
                            "percentage": 0
                        }

                    basic_analysis["asset_types"][asset_type]["count"] += 1

                    if isinstance(security.get("value", 0), (int, float)):
                        basic_analysis["asset_types"][asset_type]["total_value"] += security.get("value", 0)

                # Calculate percentages
                for asset_type, data in basic_analysis["asset_types"].items():
                    if basic_analysis["total_value"] > 0:
                        data["percentage"] = (data["total_value"] / basic_analysis["total_value"]) * 100

        return basic_analysis

    def _analyze_asset_allocation(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze asset allocation in the portfolio."""
        allocation = {
            "current_allocation": {},
            "allocation_by_sector": {},
            "allocation_by_region": {},
            "allocation_by_currency": {}
        }

        if "securities" in portfolio_data:
            securities = portfolio_data["securities"]
            total_value = portfolio_data.get("total_value", 0)

            if securities and total_value > 0:
                # Allocation by asset type
                asset_types = {}

                for security in securities:
                    asset_type = self._classify_asset_type(security)

                    if asset_type not in asset_types:
                        asset_types[asset_type] = 0

                    if isinstance(security.get("value", 0), (int, float)):
                        asset_types[asset_type] += security.get("value", 0)

                # Calculate percentages
                for asset_type, value in asset_types.items():
                    allocation["current_allocation"][asset_type] = (value / total_value) * 100

                # Try to classify by sector
                sectors = {}

                for security in securities:
                    sector = self._classify_industry_sector(security)

                    if sector not in sectors:
                        sectors[sector] = 0

                    if isinstance(security.get("value", 0), (int, float)):
                        sectors[sector] += security.get("value", 0)

                # Calculate percentages
                for sector, value in sectors.items():
                    allocation["allocation_by_sector"][sector] = (value / total_value) * 100

        return allocation

    def _analyze_performance(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze portfolio performance."""
        performance = {
            "average_return": None,
            "total_return": None,
            "best_performers": [],
            "worst_performers": []
        }

        if "securities" in portfolio_data:
            securities = portfolio_data["securities"]
            securities_with_return = [sec for sec in securities
                                   if isinstance(sec.get("return", None), (int, float))]

            if securities_with_return:
                # Calculate average return
                returns = [sec["return"] for sec in securities_with_return]
                performance["average_return"] = sum(returns) / len(returns)

                # Find best and worst performers
                sorted_by_return = sorted(securities_with_return, key=lambda x: x["return"], reverse=True)

                performance["best_performers"] = sorted_by_return[:3]
                performance["worst_performers"] = sorted_by_return[-3:] if len(sorted_by_return) > 3 else sorted_by_return[::-1]

                # Calculate weighted total return
                if portfolio_data.get("total_value", 0) > 0:
                    weighted_returns = []

                    for security in securities_with_return:
                        if isinstance(security.get("value", 0), (int, float)) and security["value"] > 0:
                            weight = security["value"] / portfolio_data["total_value"]
                            weighted_return = security["return"] * weight
                            weighted_returns.append(weighted_return)

                    if weighted_returns:
                        performance["total_return"] = sum(weighted_returns)

        return performance

    def _analyze_risk(self, portfolio_data: Dict[str, Any], risk_profile: str) -> Dict[str, Any]:
        """Analyze portfolio risk."""
        risk_analysis = {
            "risk_level": "unknown",
            "concentration_risk": [],
            "risk_metrics": {},
            "risk_profile": risk_profile,
            "risk_profile_match": None
        }

        if "securities" in portfolio_data:
            securities = portfolio_data["securities"]
            total_value = portfolio_data.get("total_value", 0)

            if securities and total_value > 0:
                # Check concentration
                for security in securities:
                    if isinstance(security.get("value", 0), (int, float)) and security["value"] > 0:
                        percentage = (security["value"] / total_value) * 100

                        if percentage > self.risk_thresholds[risk_profile]["max_single_holding"]:
                            risk_analysis["concentration_risk"].append({
                                "security_name": security.get("name", security.get("security_name", "")),
                                "isin": security.get("isin", ""),
                                "percentage": percentage,
                                "threshold": self.risk_thresholds[risk_profile]["max_single_holding"]
                            })

                # Analyze risk by asset allocation
                allocation = self._analyze_asset_allocation(portfolio_data)
                current_allocation = allocation["current_allocation"]

                # Calculate risk score
                risk_score = self._calculate_risk_score(current_allocation)
                risk_analysis["risk_metrics"]["risk_score"] = risk_score

                # Determine risk level
                if risk_score < 25:
                    risk_analysis["risk_level"] = "low"
                elif risk_score < 50:
                    risk_analysis["risk_level"] = "medium"
                else:
                    risk_analysis["risk_level"] = "high"

                # Check profile match
                risk_analysis["risk_profile_match"] = (risk_analysis["risk_level"] == risk_profile)

        return risk_analysis

    def _calculate_risk_score(self, asset_allocation: Dict[str, float]) -> float:
        """Calculate risk score based on asset allocation."""
        risk_weights = {
            "stocks": 80,
            "bonds": 30,
            "cash": 5,
            "etf": 60,
            "funds": 50,
            "real_estate": 70,
            "commodities": 75,
            "alternatives": 90,
            "unknown": 50
        }

        risk_score = 0
        total_percentage = 0

        for asset_type, percentage in asset_allocation.items():
            weight = risk_weights.get(asset_type, risk_weights["unknown"])
            risk_score += weight * percentage
            total_percentage += percentage

        if total_percentage > 0:
            return risk_score / total_percentage

        return 0

    def _classify_asset_type(self, security: Dict[str, Any]) -> str:
        """Classify asset type."""
        # Look for explicit type
        if "type" in security:
            security_type = str(security["type"]).lower()

            for asset_class, keywords in self.asset_classes.items():
                if any(keyword in security_type for keyword in keywords):
                    return asset_class

        # Look in security name
        if "name" in security or "security_name" in security:
            security_name = str(security.get("name", security.get("security_name", ""))).lower()

            for asset_class, keywords in self.asset_classes.items():
                if any(keyword in security_name for keyword in keywords):
                    return asset_class

        return "unknown"

    def _classify_industry_sector(self, security: Dict[str, Any]) -> str:
        """Classify industry sector."""
        # Look in security description
        for field in ["name", "security_name", "description", "sector", "industry"]:
            if field in security:
                value = str(security[field]).lower()

                for sector, keywords in self.industry_sectors.items():
                    if any(keyword in value for keyword in keywords):
                        return sector

        return "unknown"

    def _generate_recommendations(self, basic_analysis, asset_allocation, performance_analysis, risk_analysis, risk_profile) -> List[Dict[str, Any]]:
        """Generate investment recommendations."""
        recommendations = []

        # Diversification recommendations
        if risk_analysis["concentration_risk"]:
            for concentration in risk_analysis["concentration_risk"]:
                recommendations.append({
                    "type": "diversification",
                    "priority": "high",
                    "title": f"Reduce concentration in {concentration['security_name']}",
                    "description": f"The security represents {concentration['percentage']:.2f}% of the portfolio, above the recommended threshold of {concentration['threshold']}%.",
                    "action": f"Consider reducing the position or diversifying the risk."
                })

        # Asset allocation recommendations
        target_allocation = self._get_target_allocation(risk_profile)
        current_allocation = asset_allocation["current_allocation"]

        for asset_type, target_pct in target_allocation.items():
            current_pct = current_allocation.get(asset_type, 0)
            gap = target_pct - current_pct

            if abs(gap) >= 10:  # Significant gap
                action = "increase" if gap > 0 else "decrease"

                recommendations.append({
                    "type": "asset_allocation",
                    "priority": "medium",
                    "title": f"Adjust asset allocation: {asset_type}",
                    "description": f"Current allocation: {current_pct:.2f}%, recommended allocation: {target_pct:.2f}%.",
                    "action": f"Consider {action}ing exposure to {asset_type} by {abs(gap):.2f}%."
                })

        # Performance recommendations
        if performance_analysis.get("worst_performers"):
            for performer in performance_analysis["worst_performers"]:
                if performer.get("return", 0) < -10:  # Poor performance
                    recommendations.append({
                        "type": "performance",
                        "priority": "medium",
                        "title": f"Reevaluate {performer.get('name', performer.get('security_name', ''))}",
                        "description": f"Return of {performer.get('return', 0):.2f}%.",
                        "action": "Consider replacing with an alternative security or reevaluate the investment thesis."
                    })

        # Risk profile match recommendations
        if risk_analysis["risk_level"] != risk_profile:
            action = "reduce" if risk_analysis["risk_level"] == "high" and risk_profile in ["low", "medium"] else "increase"

            recommendations.append({
                "type": "risk_profile",
                "priority": "high",
                "title": "Adjust risk level to match investor profile",
                "description": f"Current risk level ({risk_analysis['risk_level']}) does not match the desired risk profile ({risk_profile}).",
                "action": f"Consider {action}ing portfolio risk through asset allocation changes."
            })

        return recommendations

    def _get_target_allocation(self, risk_profile: str) -> Dict[str, float]:
        """Get recommended asset allocation based on risk profile."""
        if risk_profile == "low":
            return {
                "cash": 15,
                "bonds": 55,
                "stocks": 25,
                "alternatives": 5
            }
        elif risk_profile == "medium":
            return {
                "cash": 10,
                "bonds": 35,
                "stocks": 45,
                "alternatives": 10
            }
        elif risk_profile == "high":
            return {
                "cash": 5,
                "bonds": 15,
                "stocks": 65,
                "alternatives": 15
            }
        else:
            return {
                "cash": 10,
                "bonds": 40,
                "stocks": 40,
                "alternatives": 10
            }

    def analyze_financial_statements(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze financial statements (balance sheet, income statement).

        Args:
            document_data: Processed document data

        Returns:
            Dictionary with balance sheet and income statement analysis
        """
        result = {
            "status": "error",
            "message": "No financial statement data found in the document",
            "analysis_date": datetime.now().isoformat()
        }

        # Analyze balance sheet
        balance_sheet_data = self._extract_balance_sheet_data(document_data)
        if balance_sheet_data:
            balance_analysis = self._analyze_balance_sheet(balance_sheet_data)
            result["balance_sheet_analysis"] = balance_analysis
            result["status"] = "success"
            result["message"] = None

        # Analyze income statement
        income_statement_data = self._extract_income_statement_data(document_data)
        if income_statement_data:
            income_analysis = self._analyze_income_statement(income_statement_data)
            result["income_statement_analysis"] = income_analysis
            result["status"] = "success"
            result["message"] = None

        # Analyze financial ratios
        if balance_sheet_data and income_statement_data:
            ratios_analysis = self._analyze_financial_ratios(balance_sheet_data, income_statement_data)
            result["financial_ratios"] = ratios_analysis

        return result

    def _extract_balance_sheet_data(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract balance sheet data from a document."""
        balance_data = {}

        # Look in financial data
        if "financial_data" in document_data and "balance_sheet" in document_data["financial_data"]:
            balance_data = document_data["financial_data"]["balance_sheet"]

        # Look in tables
        elif "tables" in document_data:
            for table in document_data["tables"]:
                if table.get("type") == "balance_sheet" and "data" in table:
                    balance_data = self._convert_table_to_balance_sheet(table["data"])
                    break

        return balance_data

    def _extract_income_statement_data(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract income statement data from a document."""
        income_data = {}

        # Look in financial data
        if "financial_data" in document_data and "income_statement" in document_data["financial_data"]:
            income_data = document_data["financial_data"]["income_statement"]

        # Look in tables
        elif "tables" in document_data:
            for table in document_data["tables"]:
                if table.get("type") == "income_statement" and "data" in table:
                    income_data = self._convert_table_to_income_statement(table["data"])
                    break

        return income_data

    def _convert_table_to_balance_sheet(self, table_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Convert table to balance sheet data."""
        balance_sheet = {
            "assets": {},
            "liabilities": {},
            "equity": {}
        }

        for row in table_data:
            row_type = None
            item_name = None
            item_value = None

            # Identify row type (assets, liabilities, equity)
            for key, value in row.items():
                key_lower = str(key).lower()

                # Look for item type
                if isinstance(value, str):
                    value_lower = value.lower()

                    if any(kw in value_lower for kw in ["נכסים", "רכוש", "assets"]):
                        row_type = "assets"
                        item_name = value
                    elif any(kw in value_lower for kw in ["התחייבויות", "אשראי", "liabilities"]):
                        row_type = "liabilities"
                        item_name = value
                    elif any(kw in value_lower for kw in ["הון", "equity"]):
                        row_type = "equity"
                        item_name = value

                # If we've already identified the row type, look for the numeric value
                if row_type and item_name and isinstance(value, (int, float)):
                    item_value = value
                    break
                elif row_type and item_name and isinstance(value, str):
                    # Try to parse as number
                    parsed_value = self._parse_numeric(value)
                    if parsed_value is not None:
                        item_value = parsed_value
                        break

            # Add item to balance sheet
            if row_type and item_name and item_value is not None:
                balance_sheet[row_type][item_name] = item_value

        # Calculate summaries
        balance_sheet["summary"] = {
            "total_assets": sum(balance_sheet["assets"].values()),
            "total_liabilities": sum(balance_sheet["liabilities"].values()),
            "total_equity": sum(balance_sheet["equity"].values())
        }

        return balance_sheet

    def _convert_table_to_income_statement(self, table_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Convert table to income statement data."""
        income_statement = {
            "revenues": {},
            "expenses": {},
            "profits": {}
        }

        for row in table_data:
            row_type = None
            item_name = None
            item_value = None

            # Identify row type (revenues, expenses, profits)
            for key, value in row.items():
                key_lower = str(key).lower()

                # Look for item type
                if isinstance(value, str):
                    value_lower = value.lower()

                    if any(kw in value_lower for kw in ["הכנסות", "מכירות", "revenues", "sales"]):
                        row_type = "revenues"
                        item_name = value
                    elif any(kw in value_lower for kw in ["הוצאות", "עלות", "expenses", "costs"]):
                        row_type = "expenses"
                        item_name = value
                    elif any(kw in value_lower for kw in ["רווח", "הפסד", "profit", "loss"]):
                        row_type = "profits"
                        item_name = value

                # If we've already identified the row type, look for the numeric value
                if row_type and item_name and isinstance(value, (int, float)):
                    item_value = value
                    break
                elif row_type and item_name and isinstance(value, str):
                    # Try to parse as number
                    parsed_value = self._parse_numeric(value)
                    if parsed_value is not None:
                        item_value = parsed_value
                        break

            # Add item to income statement
            if row_type and item_name and item_value is not None:
                income_statement[row_type][item_name] = item_value

        # Calculate summaries
        income_statement["summary"] = {
            "total_revenue": sum(income_statement["revenues"].values()),
            "total_expenses": sum(income_statement["expenses"].values()),
            "net_profit": sum(income_statement["revenues"].values()) - sum(income_statement["expenses"].values())
        }

        return income_statement

    def _analyze_balance_sheet(self, balance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze balance sheet."""
        analysis = {
            "total_assets": 0,
            "total_liabilities": 0,
            "total_equity": 0,
            "current_ratio": None,
            "debt_to_equity": None,
            "debt_to_assets": None,
            "major_assets": [],
            "major_liabilities": []
        }

        # Summaries
        if "summary" in balance_data:
            analysis["total_assets"] = balance_data["summary"].get("total_assets", 0)
            analysis["total_liabilities"] = balance_data["summary"].get("total_liabilities", 0)
            analysis["total_equity"] = balance_data["summary"].get("total_equity", 0)
        else:
            analysis["total_assets"] = sum(balance_data.get("assets", {}).values())
            analysis["total_liabilities"] = sum(balance_data.get("liabilities", {}).values())
            analysis["total_equity"] = sum(balance_data.get("equity", {}).values())

        # Calculate ratios
        if analysis["total_assets"] > 0:
            analysis["debt_to_assets"] = analysis["total_liabilities"] / analysis["total_assets"]

            # Identify current assets and liabilities
            current_assets = 0
            current_liabilities = 0

            for name, value in balance_data.get("assets", {}).items():
                name_lower = str(name).lower()
                if any(keyword in name_lower for keyword in ["current", "שוטף", "מזומנים", "cash"]):
                    current_assets += value

            for name, value in balance_data.get("liabilities", {}).items():
                name_lower = str(name).lower()
                if any(keyword in name_lower for keyword in ["current", "שוטף", "זכאים", "payable"]):
                    current_liabilities += value

            if current_liabilities > 0:
                analysis["current_ratio"] = current_assets / current_liabilities

        if analysis["total_equity"] > 0:
            analysis["debt_to_equity"] = analysis["total_liabilities"] / analysis["total_equity"]

        # Identify major assets and liabilities
        if "assets" in balance_data:
            sorted_assets = sorted(balance_data["assets"].items(), key=lambda x: x[1], reverse=True)
            analysis["major_assets"] = [{"name": name, "value": value} for name, value in sorted_assets[:3]]

        if "liabilities" in balance_data:
            sorted_liabilities = sorted(balance_data["liabilities"].items(), key=lambda x: x[1], reverse=True)
            analysis["major_liabilities"] = [{"name": name, "value": value} for name, value in sorted_liabilities[:3]]

        return analysis

    def _analyze_income_statement(self, income_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze income statement."""
        analysis = {
            "total_revenue": 0,
            "total_expenses": 0,
            "net_profit": 0,
            "gross_profit": None,
            "operating_profit": None,
            "profit_margin": None,
            "major_revenue_sources": [],
            "major_expenses": []
        }

        # Summaries
        if "summary" in income_data:
            analysis["total_revenue"] = income_data["summary"].get("total_revenue", 0)
            analysis["total_expenses"] = income_data["summary"].get("total_expenses", 0)
            analysis["net_profit"] = income_data["summary"].get("net_profit", 0)
        else:
            analysis["total_revenue"] = sum(income_data.get("revenues", {}).values())
            analysis["total_expenses"] = sum(income_data.get("expenses", {}).values())
            analysis["net_profit"] = analysis["total_revenue"] - analysis["total_expenses"]

        # Calculate ratios
        if analysis["total_revenue"] > 0:
            analysis["profit_margin"] = (analysis["net_profit"] / analysis["total_revenue"]) * 100

            # Look for gross profit
            gross_profit = None
            for name, value in income_data.get("profits", {}).items():
                name_lower = str(name).lower()
                if any(keyword in name_lower for keyword in ["gross", "גולמי"]):
                    gross_profit = value
                    break

            if gross_profit is not None:
                analysis["gross_profit"] = gross_profit
                analysis["gross_margin"] = (gross_profit / analysis["total_revenue"]) * 100

            # Look for operating profit
            operating_profit = None
            for name, value in income_data.get("profits", {}).items():
                name_lower = str(name).lower()
                if any(keyword in name_lower for keyword in ["operating", "תפעולי"]):
                    operating_profit = value
                    break

            if operating_profit is not None:
                analysis["operating_profit"] = operating_profit
                analysis["operating_margin"] = (operating_profit / analysis["total_revenue"]) * 100

        # Identify major revenue sources and expenses
        if "revenues" in income_data:
            sorted_revenues = sorted(income_data["revenues"].items(), key=lambda x: x[1], reverse=True)
            analysis["major_revenue_sources"] = [{"name": name, "value": value} for name, value in sorted_revenues[:3]]

        if "expenses" in income_data:
            sorted_expenses = sorted(income_data["expenses"].items(), key=lambda x: x[1], reverse=True)
            analysis["major_expenses"] = [{"name": name, "value": value} for name, value in sorted_expenses[:3]]

        return analysis

    def _analyze_financial_ratios(self, balance_data: Dict[str, Any], income_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial ratios."""
        ratios = {
            "liquidity_ratios": {},
            "profitability_ratios": {},
            "efficiency_ratios": {},
            "solvency_ratios": {}
        }

        # Balance sheet summaries
        total_assets = balance_data.get("summary", {}).get("total_assets", 0)
        total_liabilities = balance_data.get("summary", {}).get("total_liabilities", 0)
        total_equity = balance_data.get("summary", {}).get("total_equity", 0)

        # Income statement summaries
        total_revenue = income_data.get("summary", {}).get("total_revenue", 0)
        net_profit = income_data.get("summary", {}).get("net_profit", 0)

        # Liquidity ratios
        current_assets = 0
        current_liabilities = 0

        for name, value in balance_data.get("assets", {}).items():
            name_lower = str(name).lower()
            if any(keyword in name_lower for keyword in ["current", "שוטף", "מזומנים", "cash"]):
                current_assets += value

        for name, value in balance_data.get("liabilities", {}).items():
            name_lower = str(name).lower()
            if any(keyword in name_lower for keyword in ["current", "שוטף", "זכאים", "payable"]):
                current_liabilities += value

        if current_liabilities > 0:
            ratios["liquidity_ratios"]["current_ratio"] = current_assets / current_liabilities

        # Profitability ratios
        if total_revenue > 0:
            ratios["profitability_ratios"]["net_profit_margin"] = (net_profit / total_revenue) * 100

        if total_assets > 0:
            ratios["profitability_ratios"]["return_on_assets"] = (net_profit / total_assets) * 100

        if total_equity > 0:
            ratios["profitability_ratios"]["return_on_equity"] = (net_profit / total_equity) * 100

        # Solvency ratios
        if total_assets > 0:
            ratios["solvency_ratios"]["debt_to_assets"] = (total_liabilities / total_assets) * 100

        if total_equity > 0:
            ratios["solvency_ratios"]["debt_to_equity"] = (total_liabilities / total_equity) * 100

        return ratios

    def analyze_salary(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze salary data.

        Args:
            document_data: Processed document data

        Returns:
            Dictionary with salary analysis
        """
        # Extract salary data
        salary_data = self._extract_salary_data(document_data)
        if not salary_data:
            return {
                "status": "error",
                "message": "No salary data found in the document"
            }

        # Basic salary analysis
        basic_analysis = self._analyze_basic_salary(salary_data)

        # Pension contributions analysis
        pension_analysis = self._analyze_pension_contributions(salary_data)

        # Tax analysis
        tax_analysis = self._analyze_tax(salary_data)

        # Generate recommendations
        recommendations = self._generate_salary_recommendations(basic_analysis, pension_analysis, tax_analysis)

        return {
            "status": "success",
            "analysis_date": datetime.now().isoformat(),
            "basic_analysis": basic_analysis,
            "pension_analysis": pension_analysis,
            "tax_analysis": tax_analysis,
            "recommendations": recommendations
        }

    def _extract_salary_data(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract salary data from a document."""
        salary_data = {
            "gross_salary": 0,
            "net_salary": 0,
            "deductions": {},
            "additions": {},
            "details": {}
        }

        # Look in tables
        if "tables" in document_data:
            for table in document_data["tables"]:
                # Check if it's a salary table
                if "data" in table:
                    # Look for keywords in columns
                    is_salary_table = False

                    if "columns" in table:
                        columns = table["columns"]
                        salary_keywords = ["שכר", "ברוטו", "נטו", "מס הכנסה", "ביטוח לאומי", "פנסיה", "salary", "gross", "net", "tax", "pension"]

                        if any(any(keyword in str(col).lower() for keyword in salary_keywords) for col in columns):
                            is_salary_table = True

                    if is_salary_table:
                        salary_data = self._convert_table_to_salary_data(table["data"])
                        break

        # Look in text
        if not salary_data["gross_salary"] and "metadata" in document_data and "text" in document_data["metadata"]:
            salary_data = self._extract_salary_from_text(document_data["metadata"]["text"])

        return salary_data

    def _convert_table_to_salary_data(self, table_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Convert table to salary data."""
        salary_data = {
            "gross_salary": 0,
            "net_salary": 0,
            "deductions": {},
            "additions": {},
            "details": {}
        }

        # Map relevant fields
        salary_field_mapping = {
            "gross": ["שכר ברוטו", "ברוטו", "gross salary", "gross"],
            "net": ["שכר נטו", "נטו", "net salary", "net"],
            "income_tax": ["מס הכנסה", "מס", "income tax", "tax"],
            "social_security": ["ביטוח לאומי", "national insurance", "social security"],
            "health_insurance": ["ביטוח בריאות", "health insurance", "health"],
            "pension": ["פנסיה", "קרן פנסיה", "pension", "pension fund"],
            "further_education": ["קרן השתלמות", "השתלמות", "education fund"],
            "overtime": ["שעות נוספות", "overtime", "extra hours"],
            "vacation": ["דמי חופשה", "חופשה", "vacation", "vacation pay"],
            "sickness": ["דמי מחלה", "מחלה", "sickness", "sick pay"]
        }

        # Process the table
        for row in table_data:
            found_match = False

            for key, value in row.items():
                key_lower = str(key).lower()

                # Check for field matches
                for field_name, keywords in salary_field_mapping.items():
                    if any(kw in key_lower for kw in keywords):
                        salary_data["details"][field_name] = self._parse_numeric(value) or value
                        found_match = True

                        # Add to appropriate summaries
                        if field_name == "gross":
                            salary_data["gross_salary"] = self._parse_numeric(value) or 0
                        elif field_name == "net":
                            salary_data["net_salary"] = self._parse_numeric(value) or 0
                        elif field_name in ["income_tax", "social_security", "health_insurance", "pension", "further_education"]:
                            num_value = self._parse_numeric(value) or 0
                            if num_value > 0:
                                salary_data["deductions"][field_name] = num_value
                        elif field_name in ["overtime", "vacation", "sickness"]:
                            num_value = self._parse_numeric(value) or 0
                            if num_value > 0:
                                salary_data["additions"][field_name] = num_value

                        break

                if not found_match and isinstance(value, (int, float)):
                    # Try to identify by field name
                    for field_name, keywords in salary_field_mapping.items():
                        if any(kw in str(key).lower() for kw in keywords):
                            salary_data["details"][field_name] = value

                            # Add to appropriate summaries
                            if field_name == "gross":
                                salary_data["gross_salary"] = value
                            elif field_name == "net":
                                salary_data["net_salary"] = value
                            elif field_name in ["income_tax", "social_security", "health_insurance", "pension", "further_education"]:
                                if value > 0:
                                    salary_data["deductions"][field_name] = value
                            elif field_name in ["overtime", "vacation", "sickness"]:
                                if value > 0:
                                    salary_data["additions"][field_name] = value

                            break

        # Calculate summaries
        if salary_data["gross_salary"] > 0 and not salary_data["net_salary"]:
            # Calculate net salary if not present
            total_deductions = sum(salary_data["deductions"].values())
            salary_data["net_salary"] = salary_data["gross_salary"] - total_deductions

        return salary_data

    def _extract_salary_from_text(self, text: str) -> Dict[str, Any]:
        """Extract salary data from text."""
        salary_data = {
            "gross_salary": 0,
            "net_salary": 0,
            "deductions": {},
            "additions": {},
            "details": {}
        }

        # Look for salary data
        patterns = {
            "gross_salary": [
                r'שכר ברוטו:?\s*([\d,]+(?:\.\d+)?)',
                r'ברוטו:?\s*([\d,]+(?:\.\d+)?)',
                r'gross salary:?\s*([\d,]+(?:\.\d+)?)'
            ],
            "net_salary": [
                r'שכר נטו:?\s*([\d,]+(?:\.\d+)?)',
                r'נטו:?\s*([\d,]+(?:\.\d+)?)',
                r'net salary:?\s*([\d,]+(?:\.\d+)?)'
            ],
            "income_tax": [
                r'מס הכנסה:?\s*([\d,]+(?:\.\d+)?)',
                r'income tax:?\s*([\d,]+(?:\.\d+)?)'
            ],
            "social_security": [
                r'ביטוח לאומי:?\s*([\d,]+(?:\.\d+)?)',
                r'social security:?\s*([\d,]+(?:\.\d+)?)'
            ],
            "pension": [
                r'פנסיה:?\s*([\d,]+(?:\.\d+)?)',
                r'pension:?\s*([\d,]+(?:\.\d+)?)'
            ]
        }

        for field, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, text)
                if match:
                    value = self._parse_numeric(match.group(1))
                    if value is not None:
                        salary_data["details"][field] = value

                        # Add to appropriate summaries
                        if field == "gross_salary":
                            salary_data["gross_salary"] = value
                        elif field == "net_salary":
                            salary_data["net_salary"] = value
                        elif field in ["income_tax", "social_security", "pension"]:
                            salary_data["deductions"][field] = value

                    break

        return salary_data

    def _analyze_basic_salary(self, salary_data: Dict[str, Any]) -> Dict[str, Any]:
        """Basic salary analysis."""
        analysis = {
            "gross_salary": salary_data.get("gross_salary", 0),
            "net_salary": salary_data.get("net_salary", 0),
            "deduction_total": sum(salary_data.get("deductions", {}).values()),
            "addition_total": sum(salary_data.get("additions", {}).values()),
            "deduction_percentage": 0,
            "effective_tax_rate": 0
        }

        # Calculate percentages
        if analysis["gross_salary"] > 0:
            analysis["deduction_percentage"] = (analysis["deduction_total"] / analysis["gross_salary"]) * 100

            # Calculate effective tax rate
            income_tax = salary_data.get("deductions", {}).get("income_tax", 0)
            if income_tax > 0:
                analysis["effective_tax_rate"] = (income_tax / analysis["gross_salary"]) * 100

        return analysis

    def _analyze_pension_contributions(self, salary_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze pension contributions."""
        analysis = {
            "pension_contribution": salary_data.get("deductions", {}).get("pension", 0),
            "further_education_contribution": salary_data.get("deductions", {}).get("further_education", 0),
            "total_saving": 0,
            "contribution_percentage": 0,
            "recommended_contribution": 0
        }

        # Calculate total savings
        analysis["total_saving"] = analysis["pension_contribution"] + analysis["further_education_contribution"]

        # Calculate contribution percentage
        gross_salary = salary_data.get("gross_salary", 0)
        if gross_salary > 0:
            analysis["contribution_percentage"] = (analysis["total_saving"] / gross_salary) * 100

            # Recommended contribution
            recommended_percentage = 20  # Recommended contribution percentage
            analysis["recommended_contribution"] = (gross_salary * recommended_percentage) / 100

        return analysis

    def _analyze_tax(self, salary_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze tax."""
        analysis = {
            "income_tax": salary_data.get("deductions", {}).get("income_tax", 0),
            "social_security": salary_data.get("deductions", {}).get("social_security", 0),
            "health_insurance": salary_data.get("deductions", {}).get("health_insurance", 0),
            "total_tax": 0,
            "tax_percentage": 0,
            "tax_bracket": None
        }

        # Calculate total tax
        analysis["total_tax"] = analysis["income_tax"] + analysis["social_security"] + analysis["health_insurance"]

        # Calculate tax percentage
        gross_salary = salary_data.get("gross_salary", 0)
        if gross_salary > 0:
            analysis["tax_percentage"] = (analysis["total_tax"] / gross_salary) * 100

            # Determine tax bracket
            if analysis["tax_percentage"] < 15:
                analysis["tax_bracket"] = "low"
            elif analysis["tax_percentage"] < 30:
                analysis["tax_bracket"] = "medium"
            else:
                analysis["tax_bracket"] = "high"

        return analysis

    def _generate_salary_recommendations(self, basic_analysis, pension_analysis, tax_analysis) -> List[Dict[str, Any]]:
        """Generate salary recommendations."""
        recommendations = []

        # Pension contribution recommendations
        if pension_analysis["contribution_percentage"] < 15:
            recommendations.append({
                "type": "pension",
                "priority": "high",
                "title": "Increase pension contribution",
                "description": f"Current contribution ({pension_analysis['contribution_percentage']:.2f}%) is below the recommended level (20%).",
                "action": f"Consider increasing your pension contribution."
            })

        # Tax recommendations
        if tax_analysis["tax_bracket"] == "high" and tax_analysis["tax_percentage"] > 35:
            recommendations.append({
                "type": "tax",
                "priority": "medium",
                "title": "Tax consultation",
                "description": f"Effective tax rate ({tax_analysis['tax_percentage']:.2f}%) is high.",
                "action": "Consider meeting with a tax advisor to explore tax reduction options."
            })

        # Further education fund recommendations
        if pension_analysis["further_education_contribution"] == 0:
            recommendations.append({
                "type": "further_education",
                "priority": "medium",
                "title": "Further education fund contribution",
                "description": "No contribution to further education fund detected.",
                "action": "Consider contributing to a further education fund to maximize tax benefits."
            })

        return recommendations

    def generate_investment_suggestion(self, document_data: Dict[str, Any], investment_amount: float = 0, risk_profile: str = "medium") -> Dict[str, Any]:
        """
        Generate investment suggestions based on document data and risk profile.

        Args:
            document_data: Processed document data
            investment_amount: Amount to invest
            risk_profile: Risk profile (low, medium, high)

        Returns:
            Dictionary with investment suggestions
        """
        # Validate risk profile
        if risk_profile not in self.risk_thresholds:
            risk_profile = "medium"

        # Analyze current portfolio if available
        portfolio_data = self._extract_portfolio_data(document_data)
        current_allocation = {}

        if portfolio_data and "securities" in portfolio_data:
            # Get current asset allocation
            allocation_analysis = self._analyze_asset_allocation(portfolio_data)
            current_allocation = allocation_analysis.get("current_allocation", {})

        # Generate target allocation based on risk profile
        target_allocation = self._get_target_allocation(risk_profile)

        # Generate investment suggestions
        suggestions = self._generate_investment_suggestions(current_allocation, target_allocation, investment_amount, risk_profile)

        return {
            "status": "success",
            "analysis_date": datetime.now().isoformat(),
            "investment_amount": investment_amount,
            "risk_profile": risk_profile,
            "current_allocation": current_allocation,
            "target_allocation": target_allocation,
            "suggestions": suggestions
        }

    def _generate_investment_suggestions(self, current_allocation: Dict[str, float], target_allocation: Dict[str, float], investment_amount: float, risk_profile: str) -> List[Dict[str, Any]]:
        """
        Generate specific investment suggestions.

        Args:
            current_allocation: Current asset allocation
            target_allocation: Target asset allocation
            investment_amount: Amount to invest
            risk_profile: Risk profile

        Returns:
            List of investment suggestions
        """
        suggestions = []

        # Calculate allocation amounts
        allocation_amounts = {}
        for asset_type, percentage in target_allocation.items():
            allocation_amounts[asset_type] = (percentage / 100) * investment_amount

        # Generate suggestions for each asset type
        for asset_type, amount in allocation_amounts.items():
            if amount > 0:
                suggestion = self._generate_asset_type_suggestion(asset_type, amount, risk_profile)
                suggestions.append(suggestion)

        # Add general advice
        suggestions.append({
            "type": "general",
            "asset_type": "general",
            "title": "Diversification Strategy",
            "description": f"For a {risk_profile} risk profile, maintain a diversified portfolio across different asset classes.",
            "allocation_percentage": 100,
            "allocation_amount": investment_amount,
            "specific_suggestions": [
                "Consider dollar-cost averaging by investing gradually over time rather than all at once.",
                "Rebalance your portfolio periodically to maintain your target asset allocation.",
                "Review your investment strategy annually or when your financial situation changes."
            ]
        })

        return suggestions

    def _generate_asset_type_suggestion(self, asset_type: str, amount: float, risk_profile: str) -> Dict[str, Any]:
        """
        Generate suggestion for a specific asset type.

        Args:
            asset_type: Asset type
            amount: Amount to invest
            risk_profile: Risk profile

        Returns:
            Suggestion dictionary
        """
        suggestion = {
            "type": "asset_type",
            "asset_type": asset_type,
            "title": f"{asset_type.capitalize()} Investment",
            "description": "",
            "allocation_percentage": 0,
            "allocation_amount": amount,
            "specific_suggestions": []
        }

        # Calculate percentage
        target_allocation = self._get_target_allocation(risk_profile)
        suggestion["allocation_percentage"] = target_allocation.get(asset_type, 0)

        # Generate specific suggestions based on asset type
        if asset_type == "stocks":
            suggestion["description"] = "Equity investments for long-term growth."

            if risk_profile == "low":
                suggestion["specific_suggestions"] = [
                    "Consider large-cap, dividend-paying stocks with stable earnings.",
                    "Look for low-volatility ETFs that track major indices.",
                    "Focus on defensive sectors like utilities, consumer staples, and healthcare."
                ]
            elif risk_profile == "medium":
                suggestion["specific_suggestions"] = [
                    "Balance between growth and value stocks across various sectors.",
                    "Consider a mix of domestic and international equity ETFs.",
                    "Include mid-cap stocks for growth potential with moderate risk."
                ]
            else:  # high
                suggestion["specific_suggestions"] = [
                    "Consider growth-oriented stocks and emerging markets for higher return potential.",
                    "Explore small-cap stocks with strong growth prospects.",
                    "Consider sector-specific ETFs in technology, healthcare, or other high-growth areas."
                ]

        elif asset_type == "bonds":
            suggestion["description"] = "Fixed income investments for stability and income."

            if risk_profile == "low":
                suggestion["specific_suggestions"] = [
                    "Focus on high-quality government and investment-grade corporate bonds.",
                    "Consider short to intermediate-term bonds to minimize interest rate risk.",
                    "Look for bond ETFs with low expense ratios for broad exposure."
                ]
            elif risk_profile == "medium":
                suggestion["specific_suggestions"] = [
                    "Mix of government, corporate, and municipal bonds.",
                    "Consider adding some high-yield bonds for increased income.",
                    "Explore international bonds for diversification."
                ]
            else:  # high
                suggestion["specific_suggestions"] = [
                    "Higher allocation to corporate and high-yield bonds for increased returns.",
                    "Consider emerging market bonds for growth potential.",
                    "Look for convertible bonds that offer equity upside potential."
                ]

        elif asset_type == "cash":
            suggestion["description"] = "Cash and cash equivalents for liquidity and safety."

            suggestion["specific_suggestions"] = [
                "Keep emergency funds in high-yield savings accounts.",
                "Consider money market funds for slightly higher yields with minimal risk.",
                "Use certificates of deposit (CDs) for funds not needed immediately."
            ]

        elif asset_type == "alternatives":
            suggestion["description"] = "Alternative investments for diversification and potential higher returns."

            if risk_profile == "low":
                suggestion["specific_suggestions"] = [
                    "Consider REITs for real estate exposure with regular income.",
                    "Look for low-volatility alternative ETFs.",
                    "Explore inflation-protected securities for wealth preservation."
                ]
            elif risk_profile == "medium":
                suggestion["specific_suggestions"] = [
                    "Consider a mix of REITs, commodities, and infrastructure investments.",
                    "Explore market-neutral or long-short funds for reduced correlation with traditional markets.",
                    "Look into precious metals as a hedge against inflation and market volatility."
                ]
            else:  # high
                suggestion["specific_suggestions"] = [
                    "Consider private equity or venture capital funds for high growth potential.",
                    "Explore hedge funds with various strategies for diversification.",
                    "Look into specialized REITs or real estate crowdfunding platforms."
                ]

        return suggestion

    def _parse_numeric(self, value) -> Optional[float]:
        """Parse a value to a number."""
        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            # Remove non-numeric characters
            clean_val = re.sub(r'[^\d.-]', '', value.replace(',', ''))

            try:
                return float(clean_val)
            except (ValueError, TypeError):
                pass

        return None
