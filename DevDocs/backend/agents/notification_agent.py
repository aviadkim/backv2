"""
Notification Agent for creating user notifications based on document data.
"""
from datetime import datetime, timedelta
import re
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent

class NotificationAgent(BaseAgent):
    """Agent for creating user notifications based on document data."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the notification agent.
        
        Args:
            api_key: OpenRouter API key
            **kwargs: Additional parameters for the base agent
        """
        super().__init__(name="Notification Agent")
        self.api_key = api_key
        self.description = "I create user notifications based on document data."
        
        # Notification types
        self.notification_types = {
            "portfolio_threshold": "Portfolio value threshold alert",
            "security_performance": "Security performance",
            "expiring_security": "Security approaching maturity",
            "document_processing": "Document processing",
            "abnormal_change": "Abnormal change in portfolio",
            "custom_alert": "Custom alert"
        }
        
        # Expiry date keywords in securities
        self.expiry_keywords = [
            "תאריך פדיון", "פדיון", "מועד פירעון", "maturity", "expiry", "expiration"
        ]
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task to generate notifications.
        
        Args:
            task: Task dictionary with the following keys:
                - document_data: Processed document data
                - user_settings: User notification settings (optional)
                
        Returns:
            Dictionary with generated notifications
        """
        # Get the required data
        document_data = task.get('document_data', {})
        user_settings = task.get('user_settings', {})
        
        # Generate notifications
        notifications = self.generate_notifications(document_data, user_settings)
        
        return {
            'notifications': notifications
        }
    
    def generate_notifications(self, document_data: Dict[str, Any], user_settings: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Generate notifications based on document data and user settings.
        
        Args:
            document_data: Processed document data
            user_settings: User notification settings (optional)
            
        Returns:
            List of notifications
        """
        notifications = []
        
        # Document processing notification
        notifications.append(self._create_processing_notification(document_data))
        
        # Portfolio alerts, if there is appropriate data
        portfolio_notifications = self._check_portfolio_alerts(document_data, user_settings)
        notifications.extend(portfolio_notifications)
        
        # Specific security alerts
        security_notifications = self._check_security_alerts(document_data, user_settings)
        notifications.extend(security_notifications)
        
        # Alerts for securities approaching maturity
        expiry_notifications = self._check_expiry_alerts(document_data)
        notifications.extend(expiry_notifications)
        
        # Alerts for abnormal changes
        abnormal_notifications = self._check_abnormal_changes(document_data, user_settings)
        notifications.extend(abnormal_notifications)
        
        return notifications
    
    def _create_processing_notification(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a notification about document processing completion."""
        doc_id = document_data.get("document_id", "unknown")
        doc_type = "unknown"
        
        if "metadata" in document_data and "document_type" in document_data["metadata"]:
            doc_type = document_data["metadata"]["document_type"]
        
        return {
            "id": f"proc_{doc_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "type": "document_processing",
            "title": f"Processing of {doc_type} document completed",
            "message": f"Document processing completed successfully. You can now view the data and perform analyses.",
            "created_at": datetime.now().isoformat(),
            "priority": "normal",
            "read": False,
            "data": {
                "document_id": doc_id,
                "document_type": doc_type
            }
        }
    
    def _check_portfolio_alerts(self, document_data: Dict[str, Any], user_settings: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check and generate portfolio-related alerts."""
        notifications = []
        
        # Default settings if no user settings are provided
        default_settings = {
            "portfolio_value_threshold": 0,  # Don't alert by default
            "portfolio_change_threshold": 5.0  # Alert on 5%+ change
        }
        
        # Use user settings if available, otherwise use defaults
        settings = user_settings or {}
        for key, default_value in default_settings.items():
            if key not in settings:
                settings[key] = default_value
        
        # Check portfolio value threshold alert
        portfolio_value = None
        
        # Try to find the portfolio value
        if "financial_data" in document_data and "portfolio" in document_data["financial_data"]:
            portfolio = document_data["financial_data"]["portfolio"]
            if "summary" in portfolio and "total_value" in portfolio["summary"]:
                portfolio_value = portfolio["summary"]["total_value"]
        
        # If not found, try to look in the summary
        if portfolio_value is None and "summary" in document_data:
            doc_summary = document_data["summary"]
            if "total_portfolio_value" in doc_summary:
                portfolio_value = doc_summary["total_portfolio_value"]
        
        # Check threshold alert if there is a portfolio value and a threshold is set
        if portfolio_value is not None and settings["portfolio_value_threshold"] > 0:
            threshold = float(settings["portfolio_value_threshold"])
            
            if portfolio_value < threshold:
                notifications.append({
                    "id": f"port_val_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "type": "portfolio_threshold",
                    "title": "Portfolio value threshold alert",
                    "message": f"Portfolio value ({portfolio_value:,.2f}) is below the defined threshold ({threshold:,.2f}).",
                    "created_at": datetime.now().isoformat(),
                    "priority": "high",
                    "read": False,
                    "data": {
                        "portfolio_value": portfolio_value,
                        "threshold": threshold,
                        "difference": threshold - portfolio_value
                    }
                })
        
        return notifications
    
    def _check_security_alerts(self, document_data: Dict[str, Any], user_settings: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check and generate security-specific alerts."""
        notifications = []
        
        # Default settings if no user settings are provided
        default_settings = {
            "security_return_threshold": 10.0,  # Alert on 10%+ return/loss
            "watched_securities": []  # List of securities to watch
        }
        
        # Use user settings if available, otherwise use defaults
        settings = user_settings or {}
        for key, default_value in default_settings.items():
            if key not in settings:
                settings[key] = default_value
        
        # Collect securities from the document
        securities = []
        
        # Search in financial data
        if "financial_data" in document_data:
            financial_data = document_data["financial_data"]
            if "portfolio" in financial_data and "securities" in financial_data["portfolio"]:
                securities = financial_data["portfolio"]["securities"]
        
        # If none found, search in entities
        if not securities and "entities" in document_data:
            if "isin" in document_data["entities"]:
                securities = document_data["entities"]["isin"]
        
        # Check each security
        for security in securities:
            # Check return
            if "return" in security:
                return_value = security["return"]
                if isinstance(return_value, str):
                    # Try to convert to a number
                    try:
                        return_value = float(return_value.replace('%', '').replace(',', ''))
                    except:
                        continue
                
                if isinstance(return_value, (int, float)):
                    threshold = float(settings["security_return_threshold"])
                    
                    # Alert on abnormal return/loss
                    if abs(return_value) >= threshold:
                        security_name = security.get("name", security.get("security_name", ""))
                        isin = security.get("isin", "")
                        
                        message = ""
                        if return_value >= threshold:
                            message = f"Security {security_name} achieved an abnormal positive return of {return_value:.2f}%."
                        else:
                            message = f"Security {security_name} recorded an abnormal loss of {abs(return_value):.2f}%."
                        
                        notifications.append({
                            "id": f"sec_ret_{isin}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                            "type": "security_performance",
                            "title": "Abnormal security performance",
                            "message": message,
                            "created_at": datetime.now().isoformat(),
                            "priority": "medium",
                            "read": False,
                            "data": {
                                "security_name": security_name,
                                "isin": isin,
                                "return": return_value,
                                "threshold": threshold
                            }
                        })
            
            # Check watched securities
            if settings["watched_securities"]:
                security_id = security.get("isin", "")
                if security_id and security_id in settings["watched_securities"]:
                    security_name = security.get("name", security.get("security_name", ""))
                    
                    notifications.append({
                        "id": f"watch_{security_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "type": "custom_alert",
                        "title": "Update for watched security",
                        "message": f"Updated information detected for {security_name} ({security_id}) which is on your watch list.",
                        "created_at": datetime.now().isoformat(),
                        "priority": "low",
                        "read": False,
                        "data": {
                            "security_name": security_name,
                            "isin": security_id,
                            "security_data": security
                        }
                    })
        
        return notifications
    
    def _check_expiry_alerts(self, document_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check and generate alerts for securities approaching maturity."""
        notifications = []
        
        # Collect securities from the document
        securities = []
        
        # Search in financial data
        if "financial_data" in document_data:
            financial_data = document_data["financial_data"]
            if "portfolio" in financial_data and "securities" in financial_data["portfolio"]:
                securities = financial_data["portfolio"]["securities"]
        
        # Find securities with expiry dates
        for security in securities:
            expiry_date = None
            
            # Look for expiry date
            for key, value in security.items():
                key_lower = str(key).lower()
                if any(keyword in key_lower for keyword in self.expiry_keywords):
                    expiry_date = value
                    break
            
            if expiry_date:
                # Try to convert to a date
                parsed_date = self._parse_date(expiry_date)
                
                if parsed_date:
                    # Check if maturity is within 30 days
                    today = datetime.now().date()
                    days_to_expiry = (parsed_date - today).days
                    
                    if 0 < days_to_expiry <= 30:
                        security_name = security.get("name", security.get("security_name", ""))
                        isin = security.get("isin", "")
                        
                        notifications.append({
                            "id": f"exp_{isin}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                            "type": "expiring_security",
                            "title": f"Security approaching maturity in {days_to_expiry} days",
                            "message": f"Security {security_name} will mature on {parsed_date.strftime('%d/%m/%Y')}.",
                            "created_at": datetime.now().isoformat(),
                            "priority": "high" if days_to_expiry <= 7 else "medium",
                            "read": False,
                            "data": {
                                "security_name": security_name,
                                "isin": isin,
                                "expiry_date": parsed_date.isoformat(),
                                "days_to_expiry": days_to_expiry
                            }
                        })
        
        return notifications
    
    def _check_abnormal_changes(self, document_data: Dict[str, Any], user_settings: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check and generate alerts for abnormal changes in the portfolio."""
        notifications = []
        
        # Default settings if no user settings are provided
        default_settings = {
            "abnormal_change_threshold": 20.0  # Alert on 20%+ change
        }
        
        # Use user settings if available, otherwise use defaults
        settings = user_settings or {}
        for key, default_value in default_settings.items():
            if key not in settings:
                settings[key] = default_value
        
        # Look for abnormal changes in tables
        if "tables" in document_data:
            for table in document_data["tables"]:
                if "type" in table and table["type"] == "portfolio":
                    if "data" in table:
                        for row in table["data"]:
                            # Look for a change column or percentage change
                            change_value = None
                            security_name = None
                            
                            for key, value in row.items():
                                key_lower = str(key).lower()
                                if "שינוי" in key_lower or "change" in key_lower or "%" in key_lower:
                                    if isinstance(value, (int, float)):
                                        change_value = value
                                    elif isinstance(value, str):
                                        try:
                                            # Try to convert to a number
                                            change_value = float(value.replace('%', '').replace(',', ''))
                                        except:
                                            pass
                                elif "שם" in key_lower or "name" in key_lower or "תיאור" in key_lower:
                                    security_name = value
                            
                            # Check alert if there is a change value and a threshold is set
                            if change_value is not None and security_name:
                                threshold = float(settings["abnormal_change_threshold"])
                                
                                if abs(change_value) >= threshold:
                                    direction = "increase" if change_value >= 0 else "decrease"
                                    
                                    notifications.append({
                                        "id": f"change_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                                        "type": "abnormal_change",
                                        "title": f"Abnormal {direction} in security",
                                        "message": f"Security {security_name} recorded an abnormal {direction} of {abs(change_value):.2f}%.",
                                        "created_at": datetime.now().isoformat(),
                                        "priority": "high",
                                        "read": False,
                                        "data": {
                                            "security_name": security_name,
                                            "change": change_value,
                                            "threshold": threshold
                                        }
                                    })
        
        return notifications
    
    def _parse_date(self, date_str):
        """Try to parse a date from a string."""
        if not date_str:
            return None
            
        # Common date formats
        date_formats = [
            # DD/MM/YYYY
            r'(\d{1,2})[/\.-](\d{1,2})[/\.-](\d{2,4})',
            # YYYY-MM-DD
            r'(\d{4})[/\.-](\d{1,2})[/\.-](\d{1,2})'
        ]
        
        for pattern in date_formats:
            match = re.search(pattern, str(date_str))
            if match:
                groups = match.groups()
                
                # Check the date format
                if len(groups) == 3:
                    if len(groups[0]) == 4:  # YYYY-MM-DD
                        year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                    else:  # DD/MM/YYYY
                        day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
                        
                        # Handle two-digit year
                        if year < 100:
                            year += 2000 if year < 50 else 1900
                    
                    try:
                        return datetime(year, month, day).date()
                    except ValueError:
                        continue
        
        return None
