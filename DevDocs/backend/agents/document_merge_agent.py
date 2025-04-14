from datetime import datetime
from typing import Dict, List, Any, Optional
import re

class DocumentMergeAgent:
    """סוכן לאיחוד מידע ממספר דוחות/מסמכים לכדי תמונה כוללת."""

    def __init__(self):
        # סוגי מסמכים שהסוכן יודע לאחד
        self.supported_document_types = [
            "portfolio_statement",  # דוח תיק השקעות
            "balance_sheet",        # מאזן
            "income_statement",     # דוח רווח והפסד
            "bank_statement",       # דף חשבון בנק
            "salary_statement"      # תלוש שכר
        ]

    def merge_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        איחוד מסמכים לכדי מסמך אחד.

        Args:
            documents: רשימת מסמכים מעובדים

        Returns:
            מסמך מאוחד עם כל המידע
        """
        if not documents:
            return {"status": "error", "message": "לא סופקו מסמכים לאיחוד"}

        # סיווג המסמכים לפי סוג
        documents_by_type = self._classify_documents(documents)

        # איחוד נתונים לפי סוג
        merged_document = {
            "merge_date": datetime.now().isoformat(),
            "original_documents": len(documents),
            "document_types": list(documents_by_type.keys()),
            "merged_data": {},
            "summary": {}
        }

        # איחוד לפי סוג מסמך
        for doc_type, docs in documents_by_type.items():
            if doc_type == "portfolio_statement":
                merged_document["merged_data"]["portfolio"] = self._merge_portfolio_statements(docs)
            elif doc_type == "balance_sheet":
                merged_document["merged_data"]["balance_sheet"] = self._merge_balance_sheets(docs)
            elif doc_type == "income_statement":
                merged_document["merged_data"]["income_statement"] = self._merge_income_statements(docs)
            elif doc_type == "bank_statement":
                merged_document["merged_data"]["bank_statements"] = self._merge_bank_statements(docs)
            elif doc_type == "salary_statement":
                merged_document["merged_data"]["salary"] = self._merge_salary_statements(docs)

        # יצירת סיכום מאוחד
        merged_document["summary"] = self._create_merged_summary(merged_document["merged_data"])

        return merged_document

    def compare_merged_document_over_time(self, merged_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        השוואת מסמכים מאוחדים לאורך זמן.

        Args:
            merged_documents: רשימת מסמכים מאוחדים ממוינת לפי תאריך

        Returns:
            השוואה וניתוח מגמות לאורך זמן
        """
        if len(merged_documents) < 2:
            return {"status": "error", "message": "נדרשים לפחות שני מסמכים מאוחדים להשוואה לאורך זמן"}

        # מיון המסמכים לפי תאריך
        sorted_documents = sorted(merged_documents, key=lambda x: x.get("merge_date", ""))

        comparison = {
            "comparison_date": datetime.now().isoformat(),
            "period_start": sorted_documents[0].get("merge_date", ""),
            "period_end": sorted_documents[-1].get("merge_date", ""),
            "document_count": len(sorted_documents),
            "trends": {},
            "summary": {}
        }

        # ניתוח מגמות לפי סוג נתונים
        if all("merged_data" in doc and "portfolio" in doc["merged_data"] for doc in sorted_documents):
            comparison["trends"]["portfolio"] = self._analyze_portfolio_trends(
                [doc["merged_data"]["portfolio"] for doc in sorted_documents]
            )

        if all("merged_data" in doc and "balance_sheet" in doc["merged_data"] for doc in sorted_documents):
            comparison["trends"]["balance_sheet"] = self._analyze_balance_sheet_trends(
                [doc["merged_data"]["balance_sheet"] for doc in sorted_documents]
            )

        if all("merged_data" in doc and "income_statement" in doc["merged_data"] for doc in sorted_documents):
            comparison["trends"]["income_statement"] = self._analyze_income_statement_trends(
                [doc["merged_data"]["income_statement"] for doc in sorted_documents]
            )

        if all("merged_data" in doc and "salary" in doc["merged_data"] for doc in sorted_documents):
            comparison["trends"]["salary"] = self._analyze_salary_trends(
                [doc["merged_data"]["salary"] for doc in sorted_documents]
            )

        # יצירת סיכום מגמות
        comparison["summary"] = self._create_trends_summary(comparison["trends"])

        return comparison

    def generate_comprehensive_report(self, merged_document: Dict[str, Any]) -> Dict[str, Any]:
        """
        יצירת דוח מקיף המשלב את כל המידע הפיננסי.

        Args:
            merged_document: מסמך מאוחד

        Returns:
            דוח מקיף עם ניתוח פיננסי משולב
        """
        report = {
            "report_date": datetime.now().isoformat(),
            "report_type": "comprehensive_financial_report",
            "data_sources": merged_document.get("document_types", []),
            "financial_snapshot": {},
            "assets_and_liabilities": {},
            "income_and_expenses": {},
            "investments": {},
            "recommendations": []
        }

        # יצירת תמונת מצב פיננסית
        report["financial_snapshot"] = self._create_financial_snapshot(merged_document["merged_data"])

        # ניתוח נכסים והתחייבויות
        report["assets_and_liabilities"] = self._analyze_assets_and_liabilities(merged_document["merged_data"])

        # ניתוח הכנסות והוצאות
        report["income_and_expenses"] = self._analyze_income_and_expenses(merged_document["merged_data"])

        # ניתוח השקעות
        report["investments"] = self._analyze_investments(merged_document["merged_data"])

        # יצירת המלצות
        report["recommendations"] = self._generate_comprehensive_recommendations(report)

        return report

    def _classify_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """סיווג מסמכים לפי סוג."""
        documents_by_type = {}

        for doc in documents:
            doc_type = "unknown"

            # ניסיון לזהות סוג מסמך ממטא-דאטה
            if "metadata" in doc and "document_type" in doc["metadata"]:
                doc_type = doc["metadata"]["document_type"]

            # אם לא נמצא במטא-דאטה, ניסיון לזהות לפי תוכן
            if doc_type == "unknown":
                doc_type = self._identify_document_type(doc)

            # הוספה לקטגוריה מתאימה
            if doc_type not in documents_by_type:
                documents_by_type[doc_type] = []

            documents_by_type[doc_type].append(doc)

        return documents_by_type

    def _identify_document_type(self, document: Dict[str, Any]) -> str:
        """זיהוי סוג מסמך לפי תוכן."""
        # זיהוי לפי טבלאות
        if "tables" in document:
            for table in document["tables"]:
                table_type = table.get("type", "")
                if table_type in ["portfolio", "portfolio_statement"]:
                    return "portfolio_statement"
                elif table_type in ["balance_sheet", "balance"]:
                    return "balance_sheet"
                elif table_type in ["income_statement", "profit_and_loss"]:
                    return "income_statement"
                elif table_type in ["bank_statement", "account"]:
                    return "bank_statement"

        # זיהוי לפי נתונים פיננסיים
        if "financial_data" in document:
            if "portfolio" in document["financial_data"]:
                return "portfolio_statement"
            elif "balance_sheet" in document["financial_data"]:
                return "balance_sheet"
            elif "income_statement" in document["financial_data"]:
                return "income_statement"

        # זיהוי תלוש שכר
        if self._is_salary_statement(document):
            return "salary_statement"

        return "unknown"

    def _is_salary_statement(self, document: Dict[str, Any]) -> bool:
        """בדיקה אם המסמך הוא תלוש שכר."""
        # חיפוש בטבלאות
        if "tables" in document:
            for table in document["tables"]:
                # חיפוש כותרות אופייניות לתלוש שכר
                if "columns" in table:
                    salary_keywords = ["שכר", "ברוטו", "נטו", "מס הכנסה", "ביטוח לאומי"]

                    for col in table["columns"]:
                        if any(keyword in str(col).lower() for keyword in salary_keywords):
                            return True

        # חיפוש בטקסט
        if "metadata" in document and "text" in document["metadata"]:
            text = document["metadata"]["text"]
            salary_patterns = [
                r'תלוש שכר',
                r'משכורת לחודש',
                r'תשלום שכר',
                r'שכר ברוטו',
                r'salary slip',
                r'pay slip'
            ]

            for pattern in salary_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return True

        return False

    def _parse_numeric(self, value) -> Optional[float]:
        """המרת ערך למספר."""
        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            # הסרת תווים לא מספריים
            clean_val = re.sub(r'[^\d.-]', '', value.replace(',', ''))

            try:
                return float(clean_val)
            except (ValueError, TypeError):
                pass

        return None

    def _merge_portfolio_statements(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """איחוד דוחות תיק השקעות."""
        if not documents:
            return {}

        # מיון המסמכים לפי תאריך (מהמאוחר לקדום)
        sorted_docs = sorted(
            documents,
            key=lambda x: x.get("metadata", {}).get("document_date", ""),
            reverse=True
        )

        # שימוש במסמך העדכני ביותר כבסיס
        latest_doc = sorted_docs[0]

        # חילוץ נתוני תיק
        merged_portfolio = {"securities": [], "summary": {}}

        # חיפוש נתוני תיק בנתיבים שונים במסמך
        if "financial_data" in latest_doc and "portfolio" in latest_doc["financial_data"]:
            portfolio_data = latest_doc["financial_data"]["portfolio"]

            # העתקת נתוני סיכום
            if "summary" in portfolio_data:
                merged_portfolio["summary"] = portfolio_data["summary"].copy()

            # העתקת רשימת ניירות ערך
            if "securities" in portfolio_data:
                merged_portfolio["securities"] = portfolio_data["securities"].copy()

        # אם לא נמצאו נתוני תיק, חיפוש בטבלאות
        elif not merged_portfolio["securities"] and "tables" in latest_doc:
            for table in latest_doc["tables"]:
                if table.get("type") in ["portfolio", "portfolio_statement"] and "data" in table:
                    securities = []

                    for row in table["data"]:
                        security = {}

                        # המרת שורת טבלה לנייר ערך
                        for key, value in row.items():
                            key_lower = str(key).lower()

                            # שם נייר
                            if "שם" in key_lower or "name" in key_lower or "תיאור" in key_lower:
                                security["name"] = value
                            # ISIN
                            elif "isin" in key_lower:
                                security["isin"] = value
                            # סוג נייר
                            elif "סוג" in key_lower or "type" in key_lower:
                                security["type"] = value
                            # כמות
                            elif "כמות" in key_lower or "quantity" in key_lower:
                                security["quantity"] = self._parse_numeric(value)
                            # שער
                            elif "שער" in key_lower or "מחיר" in key_lower or "price" in key_lower:
                                security["price"] = self._parse_numeric(value)
                            # שווי
                            elif "שווי" in key_lower or "ערך" in key_lower or "value" in key_lower:
                                security["value"] = self._parse_numeric(value)
                            # תשואה
                            elif "תשואה" in key_lower or "return" in key_lower:
                                security["return"] = self._parse_numeric(value)

                        if security:
                            securities.append(security)

                    if securities:
                        merged_portfolio["securities"] = securities

                        # חישוב סיכום
                        total_value = sum(security.get("value", 0) for security in securities
                                       if isinstance(security.get("value", 0), (int, float)))

                        merged_portfolio["summary"]["total_value"] = total_value

                        break

        # איחוד מידע מדוחות נוספים (למשל, ביצועים היסטוריים)
        if len(sorted_docs) > 1:
            # חיפוש נתונים היסטוריים
            historical_data = self._extract_historical_data(sorted_docs[1:])
            if historical_data:
                merged_portfolio["historical_data"] = historical_data

        return merged_portfolio

    def _extract_historical_data(self, older_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """חילוץ נתונים היסטוריים מדוחות ישנים יותר."""
        historical_data = {
            "portfolio_values": [],
            "returns": []
        }

        for doc in older_documents:
            doc_date = doc.get("metadata", {}).get("document_date", "")
            if not doc_date:
                continue

            # חילוץ שווי תיק
            portfolio_value = None

            if "financial_data" in doc and "portfolio" in doc["financial_data"]:
                portfolio_data = doc["financial_data"]["portfolio"]
                if "summary" in portfolio_data and "total_value" in portfolio_data["summary"]:
                    portfolio_value = portfolio_data["summary"]["total_value"]

            # אם לא נמצא, חיפוש בסיכום מסמך
            if portfolio_value is None and "summary" in doc:
                if "total_portfolio_value" in doc["summary"]:
                    portfolio_value = doc["summary"]["total_portfolio_value"]

            if portfolio_value is not None:
                historical_data["portfolio_values"].append({
                    "date": doc_date,
                    "value": portfolio_value
                })

        # מיון לפי תאריך
        historical_data["portfolio_values"] = sorted(
            historical_data["portfolio_values"],
            key=lambda x: x["date"]
        )

        # חישוב תשואות בין תקופות
        if len(historical_data["portfolio_values"]) > 1:
            for i in range(1, len(historical_data["portfolio_values"])):
                current = historical_data["portfolio_values"][i]
                previous = historical_data["portfolio_values"][i-1]

                if previous["value"] > 0:
                    return_pct = ((current["value"] - previous["value"]) / previous["value"]) * 100

                    historical_data["returns"].append({
                        "start_date": previous["date"],
                        "end_date": current["date"],
                        "start_value": previous["value"],
                        "end_value": current["value"],
                        "return_pct": return_pct
                    })

        return historical_data

    def _merge_balance_sheets(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """איחוד מאזנים."""
        if not documents:
            return {}

        # מיון המסמכים לפי תאריך (מהמאוחר לקדום)
        sorted_docs = sorted(
            documents,
            key=lambda x: x.get("metadata", {}).get("document_date", ""),
            reverse=True
        )

        # שימוש במסמך העדכני ביותר כבסיס
        latest_doc = sorted_docs[0]

        # חילוץ נתוני מאזן
        merged_balance_sheet = {"assets": {}, "liabilities": {}, "equity": {}, "summary": {}}

        # חיפוש נתוני מאזן בנתיבים שונים במסמך
        if "financial_data" in latest_doc and "balance_sheet" in latest_doc["financial_data"]:
            balance_data = latest_doc["financial_data"]["balance_sheet"]

            # העתקת קטגוריות
            for category in ["assets", "liabilities", "equity", "summary"]:
                if category in balance_data:
                    merged_balance_sheet[category] = balance_data[category].copy()

        # אם לא נמצאו נתוני מאזן, חיפוש בטבלאות
        elif "tables" in latest_doc:
            for table in latest_doc["tables"]:
                if table.get("type") in ["balance_sheet", "balance"] and "data" in table:
                    balance_data = self._convert_table_to_balance_sheet(table["data"])

                    if balance_data:
                        for category in ["assets", "liabilities", "equity", "summary"]:
                            if category in balance_data:
                                merged_balance_sheet[category] = balance_data[category].copy()

                        break

        # איחוד מידע מדוחות נוספים (למשל, נתונים היסטוריים)
        if len(sorted_docs) > 1:
            # הוספת נתונים היסטוריים
            merged_balance_sheet["historical_data"] = self._extract_historical_balance_sheet_data(sorted_docs[1:])

        return merged_balance_sheet

    def _convert_table_to_balance_sheet(self, table_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """המרת טבלה לנתוני מאזן."""
        balance_sheet = {
            "assets": {},
            "liabilities": {},
            "equity": {}
        }

        for row in table_data:
            row_type = None
            item_name = None
            item_value = None

            # זיהוי סוג השורה (נכסים, התחייבויות, הון)
            for key, value in row.items():
                # חיפוש סוג הפריט
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

                # אם כבר זיהינו את סוג השורה, חפש את הערך המספרי
                if row_type and item_name and isinstance(value, (int, float)):
                    item_value = value
                    break
                elif row_type and item_name and isinstance(value, str):
                    # ניסיון לפרש כמספר
                    parsed_value = self._parse_numeric(value)
                    if parsed_value is not None:
                        item_value = parsed_value
                        break

            # הוספת הפריט למאזן
            if row_type and item_name and item_value is not None:
                balance_sheet[row_type][item_name] = item_value

        # חישוב סיכומים
        balance_sheet["summary"] = {
            "total_assets": sum(balance_sheet["assets"].values()),
            "total_liabilities": sum(balance_sheet["liabilities"].values()),
            "total_equity": sum(balance_sheet["equity"].values())
        }

        return balance_sheet

    def _extract_historical_balance_sheet_data(self, older_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """חילוץ נתוני מאזן היסטוריים מדוחות ישנים יותר."""
        historical_data = {
            "total_assets": [],
            "total_liabilities": [],
            "total_equity": [],
            "debt_to_equity_ratio": []
        }

        for doc in older_documents:
            doc_date = doc.get("metadata", {}).get("document_date", "")
            if not doc_date:
                continue

            balance_data = None

            # חיפוש נתוני מאזן
            if "financial_data" in doc and "balance_sheet" in doc["financial_data"]:
                balance_data = doc["financial_data"]["balance_sheet"]
            elif "tables" in doc:
                for table in doc["tables"]:
                    if table.get("type") in ["balance_sheet", "balance"] and "data" in table:
                        balance_data = self._convert_table_to_balance_sheet(table["data"])
                        break

            if balance_data and "summary" in balance_data:
                summary = balance_data["summary"]

                if "total_assets" in summary:
                    historical_data["total_assets"].append({
                        "date": doc_date,
                        "value": summary["total_assets"]
                    })

                if "total_liabilities" in summary:
                    historical_data["total_liabilities"].append({
                        "date": doc_date,
                        "value": summary["total_liabilities"]
                    })

                if "total_equity" in summary:
                    historical_data["total_equity"].append({
                        "date": doc_date,
                        "value": summary["total_equity"]
                    })

                # חישוב יחס חוב להון
                if "total_liabilities" in summary and "total_equity" in summary and summary["total_equity"] > 0:
                    ratio = summary["total_liabilities"] / summary["total_equity"]

                    historical_data["debt_to_equity_ratio"].append({
                        "date": doc_date,
                        "value": ratio
                    })

        # מיון לפי תאריך
        for key in historical_data:
            historical_data[key] = sorted(historical_data[key], key=lambda x: x["date"])

        return historical_data

    def _merge_income_statements(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """איחוד דוחות רווח והפסד."""
        if not documents:
            return {}

        # מיון המסמכים לפי תאריך (מהמאוחר לקדום)
        sorted_docs = sorted(
            documents,
            key=lambda x: x.get("metadata", {}).get("document_date", ""),
            reverse=True
        )

        # שימוש במסמך העדכני ביותר כבסיס
        latest_doc = sorted_docs[0]

        # חילוץ נתוני רווח והפסד
        merged_income_statement = {"revenues": {}, "expenses": {}, "profits": {}, "summary": {}}

        # חיפוש נתוני רווח והפסד בנתיבים שונים במסמך
        if "financial_data" in latest_doc and "income_statement" in latest_doc["financial_data"]:
            income_data = latest_doc["financial_data"]["income_statement"]

            # העתקת קטגוריות
            for category in ["revenues", "expenses", "profits", "summary"]:
                if category in income_data:
                    merged_income_statement[category] = income_data[category].copy()

        # אם לא נמצאו נתוני רווח והפסד, חיפוש בטבלאות
        elif "tables" in latest_doc:
            for table in latest_doc["tables"]:
                if table.get("type") in ["income_statement", "profit_and_loss"] and "data" in table:
                    income_data = self._convert_table_to_income_statement(table["data"])

                    if income_data:
                        for category in ["revenues", "expenses", "profits", "summary"]:
                            if category in income_data:
                                merged_income_statement[category] = income_data[category].copy()

                        break

        # איחוד מידע מדוחות נוספים (למשל, נתונים היסטוריים)
        if len(sorted_docs) > 1:
            # הוספת נתונים היסטוריים
            merged_income_statement["historical_data"] = self._extract_historical_income_data(sorted_docs[1:])

        return merged_income_statement

    def _convert_table_to_income_statement(self, table_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """המרת טבלה לנתוני דוח רווח והפסד."""
        income_statement = {
            "revenues": {},
            "expenses": {},
            "profits": {}
        }

        for row in table_data:
            row_type = None
            item_name = None
            item_value = None

            # זיהוי סוג השורה (הכנסות, הוצאות, רווחים)
            for key, value in row.items():
                # חיפוש סוג הפריט
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

                # אם כבר זיהינו את סוג השורה, חפש את הערך המספרי
                if row_type and item_name and isinstance(value, (int, float)):
                    item_value = value
                    break
                elif row_type and item_name and isinstance(value, str):
                    # ניסיון לפרש כמספר
                    parsed_value = self._parse_numeric(value)
                    if parsed_value is not None:
                        item_value = parsed_value
                        break

            # הוספת הפריט לדוח
            if row_type and item_name and item_value is not None:
                income_statement[row_type][item_name] = item_value

        # חישוב סיכומים
        income_statement["summary"] = {
            "total_revenue": sum(income_statement["revenues"].values()),
            "total_expenses": sum(income_statement["expenses"].values()),
            "net_profit": sum(income_statement["revenues"].values()) - sum(income_statement["expenses"].values())
        }

        return income_statement

    def _extract_historical_income_data(self, older_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """חילוץ נתוני רווח והפסד היסטוריים מדוחות ישנים יותר."""
        historical_data = {
            "total_revenue": [],
            "total_expenses": [],
            "net_profit": [],
            "profit_margin": []
        }

        for doc in older_documents:
            doc_date = doc.get("metadata", {}).get("document_date", "")
            if not doc_date:
                continue

            income_data = None

            # חיפוש נתוני רווח והפסד
            if "financial_data" in doc and "income_statement" in doc["financial_data"]:
                income_data = doc["financial_data"]["income_statement"]
            elif "tables" in doc:
                for table in doc["tables"]:
                    if table.get("type") in ["income_statement", "profit_and_loss"] and "data" in table:
                        income_data = self._convert_table_to_income_statement(table["data"])
                        break

            if income_data and "summary" in income_data:
                summary = income_data["summary"]

                if "total_revenue" in summary:
                    historical_data["total_revenue"].append({
                        "date": doc_date,
                        "value": summary["total_revenue"]
                    })

                if "total_expenses" in summary:
                    historical_data["total_expenses"].append({
                        "date": doc_date,
                        "value": summary["total_expenses"]
                    })

                if "net_profit" in summary:
                    historical_data["net_profit"].append({
                        "date": doc_date,
                        "value": summary["net_profit"]
                    })

                # חישוב שולי רווח
                if "total_revenue" in summary and "net_profit" in summary and summary["total_revenue"] > 0:
                    margin = (summary["net_profit"] / summary["total_revenue"]) * 100

                    historical_data["profit_margin"].append({
                        "date": doc_date,
                        "value": margin
                    })

        # מיון לפי תאריך
        for key in historical_data:
            historical_data[key] = sorted(historical_data[key], key=lambda x: x["date"])

        return historical_data

    def _merge_bank_statements(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """איחוד דפי חשבון בנק."""
        if not documents:
            return {}

        # מיון המסמכים לפי תאריך (מהמאוחר לקדום)
        sorted_docs = sorted(
            documents,
            key=lambda x: x.get("metadata", {}).get("document_date", ""),
            reverse=True
        )

        # איסוף כל העסקאות מכל המסמכים
        all_transactions = []

        for doc in sorted_docs:
            transactions = self._extract_bank_transactions(doc)
            all_transactions.extend(transactions)

        # הסרת כפילויות לפי תאריך ותיאור
        unique_transactions = self._remove_duplicate_transactions(all_transactions)

        # מיון לפי תאריך
        sorted_transactions = sorted(unique_transactions, key=lambda x: x.get("date", ""))

        # חישוב סיכומים
        summary = self._calculate_bank_summary(sorted_transactions)

        return {
            "transactions": sorted_transactions,
            "summary": summary
        }

    def _extract_bank_transactions(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """חילוץ עסקאות בנק ממסמך."""
        transactions = []

        # חיפוש בטבלאות
        if "tables" in document:
            for table in document["tables"]:
                if table.get("type") in ["bank_statement", "account", "transactions"] and "data" in table:
                    # עיבוד כל שורה כעסקה
                    for row in table["data"]:
                        transaction = {}

                        for key, value in row.items():
                            key_lower = str(key).lower()

                            # תאריך
                            if "תאריך" in key_lower or "date" in key_lower:
                                transaction["date"] = value
                            # תיאור
                            elif "תיאור" in key_lower or "description" in key_lower or "פרטים" in key_lower:
                                transaction["description"] = value
                            # סכום
                            elif "סכום" in key_lower or "amount" in key_lower:
                                transaction["amount"] = self._parse_numeric(value)
                            # זכות
                            elif "זכות" in key_lower or "credit" in key_lower:
                                amount = self._parse_numeric(value)
                                if amount is not None and amount != 0:
                                    transaction["amount"] = amount
                            # חובה
                            elif "חובה" in key_lower or "debit" in key_lower:
                                amount = self._parse_numeric(value)
                                if amount is not None and amount != 0:
                                    transaction["amount"] = -amount  # סימון שלילי לחיוב
                            # יתרה
                            elif "יתרה" in key_lower or "balance" in key_lower:
                                transaction["balance"] = self._parse_numeric(value)

                        # הוספת העסקה רק אם יש לה תאריך וסכום
                        if "date" in transaction and "amount" in transaction:
                            transactions.append(transaction)

        return transactions

    def _remove_duplicate_transactions(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """הסרת עסקאות כפולות."""
        unique_transactions = {}

        for transaction in transactions:
            # יצירת מפתח ייחודי לפי תאריך, תיאור וסכום
            date = transaction.get("date", "")
            description = transaction.get("description", "")
            amount = transaction.get("amount", 0)

            key = f"{date}_{description}_{amount}"

            # שמירת העסקה רק אם לא ראינו כבר מפתח זהה
            if key not in unique_transactions:
                unique_transactions[key] = transaction

        return list(unique_transactions.values())

    def _calculate_bank_summary(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """חישוב סיכום עסקאות בנק."""
        summary = {
            "total_credits": 0,
            "total_debits": 0,
            "net_change": 0,
            "start_balance": None,
            "end_balance": None,
            "transaction_count": len(transactions)
        }

        for transaction in transactions:
            amount = transaction.get("amount", 0)

            if amount > 0:
                summary["total_credits"] += amount
            else:
                summary["total_debits"] += abs(amount)

            # יתרה התחלתית וסופית
            if "balance" in transaction:
                if summary["start_balance"] is None or transaction["date"] < transactions[0]["date"]:
                    summary["start_balance"] = transaction["balance"] - transaction["amount"]

                if summary["end_balance"] is None or transaction["date"] > transactions[-1]["date"]:
                    summary["end_balance"] = transaction["balance"]

        summary["net_change"] = summary["total_credits"] - summary["total_debits"]

        return summary

    def _merge_salary_statements(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """איחוד תלושי שכר."""
        if not documents:
            return {}

        # מיון המסמכים לפי תאריך (מהמאוחר לקדום)
        sorted_docs = sorted(
            documents,
            key=lambda x: x.get("metadata", {}).get("document_date", ""),
            reverse=True
        )

        # יצירת רשימת תלושים
        salary_slips = []

        for doc in sorted_docs:
            # חילוץ נתוני שכר
            salary_data = self._extract_salary_data_from_document(doc)

            if salary_data:
                # הוספת תאריך המסמך
                salary_data["date"] = doc.get("metadata", {}).get("document_date", "")

                # הוספת לרשימת התלושים
                salary_slips.append(salary_data)

        # חישוב סיכומים ומגמות
        summary = self._calculate_salary_summary(salary_slips)

        return {
            "salary_slips": salary_slips,
            "summary": summary
        }

    def _extract_salary_data_from_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """חילוץ נתוני שכר ממסמך."""
        salary_data = {
            "gross_salary": 0,
            "net_salary": 0,
            "deductions": {},
            "additions": {},
            "details": {}
        }

        # חיפוש בטבלאות
        if "tables" in document:
            for table in document["tables"]:
                # חיפוש טבלת שכר
                is_salary_table = False

                if "columns" in table:
                    columns = table["columns"]
                    salary_keywords = ["שכר", "ברוטו", "נטו", "מס הכנסה", "ביטוח לאומי"]

                    if any(any(keyword in str(col).lower() for keyword in salary_keywords) for col in columns):
                        is_salary_table = True

                if is_salary_table and "data" in table:
                    # עיבוד הטבלה
                    for row in table["data"]:
                        for key, value in row.items():
                            key_lower = str(key).lower()

                            # ברוטו
                            if "ברוטו" in key_lower or "gross" in key_lower:
                                salary_data["gross_salary"] = self._parse_numeric(value) or 0
                            # נטו
                            elif "נטו" in key_lower or "net" in key_lower:
                                salary_data["net_salary"] = self._parse_numeric(value) or 0
                            # מס הכנסה
                            elif "מס הכנסה" in key_lower or "income tax" in key_lower:
                                amount = self._parse_numeric(value) or 0
                                if amount > 0:
                                    salary_data["deductions"]["income_tax"] = amount
                            # ביטוח לאומי
                            elif "ביטוח לאומי" in key_lower or "social security" in key_lower:
                                amount = self._parse_numeric(value) or 0
                                if amount > 0:
                                    salary_data["deductions"]["social_security"] = amount
                            # ביטוח בריאות
                            elif "ביטוח בריאות" in key_lower or "health" in key_lower:
                                amount = self._parse_numeric(value) or 0
                                if amount > 0:
                                    salary_data["deductions"]["health_insurance"] = amount
                            # פנסיה
                            elif "פנסיה" in key_lower or "pension" in key_lower:
                                amount = self._parse_numeric(value) or 0
                                if amount > 0:
                                    salary_data["deductions"]["pension"] = amount
                            # קרן השתלמות
                            elif "השתלמות" in key_lower or "education" in key_lower:
                                amount = self._parse_numeric(value) or 0
                                if amount > 0:
                                    salary_data["deductions"]["further_education"] = amount
                            # שעות נוספות
                            elif "שעות נוספות" in key_lower or "overtime" in key_lower:
                                amount = self._parse_numeric(value) or 0
                                if amount > 0:
                                    salary_data["additions"]["overtime"] = amount
                            # חופשה
                            elif "חופשה" in key_lower or "vacation" in key_lower:
                                amount = self._parse_numeric(value) or 0
                                if amount > 0:
                                    salary_data["additions"]["vacation"] = amount
                            # מחלה
                            elif "מחלה" in key_lower or "sickness" in key_lower:
                                amount = self._parse_numeric(value) or 0
                                if amount > 0:
                                    salary_data["additions"]["sickness"] = amount

        # חישוב סיכומים
        if salary_data["gross_salary"] > 0 and not salary_data["net_salary"]:
            # חישוב שכר נטו אם אינו קיים
            total_deductions = sum(salary_data["deductions"].values())
            salary_data["net_salary"] = salary_data["gross_salary"] - total_deductions

        return salary_data

    def _calculate_salary_summary(self, salary_slips: List[Dict[str, Any]]) -> Dict[str, Any]:
        """חישוב סיכום וניתוח תלושי שכר."""
        summary = {
            "average_gross": 0,
            "average_net": 0,
            "total_gross": 0,
            "total_net": 0,
            "period_start": None,
            "period_end": None,
            "salary_slips_count": len(salary_slips),
            "trends": {}
        }

        if not salary_slips:
            return summary

        # מיון לפי תאריך
        sorted_slips = sorted(salary_slips, key=lambda x: x.get("date", ""))

        # הגדרת תקופה
        if sorted_slips[0].get("date"):
            summary["period_start"] = sorted_slips[0]["date"]

        if sorted_slips[-1].get("date"):
            summary["period_end"] = sorted_slips[-1]["date"]

        # חישוב סיכומים
        for slip in salary_slips:
            summary["total_gross"] += slip.get("gross_salary", 0)
            summary["total_net"] += slip.get("net_salary", 0)

        if salary_slips:
            summary["average_gross"] = summary["total_gross"] / len(salary_slips)
            summary["average_net"] = summary["total_net"] / len(salary_slips)

        # ניתוח מגמות
        if len(sorted_slips) > 1:
            # מגמת שכר ברוטו
            gross_values = [slip.get("gross_salary", 0) for slip in sorted_slips]
            summary["trends"]["gross_salary"] = {
                "values": gross_values,
                "change": gross_values[-1] - gross_values[0],
                "change_pct": ((gross_values[-1] - gross_values[0]) / gross_values[0]) * 100 if gross_values[0] > 0 else 0
            }

            # מגמת שכר נטו
            net_values = [slip.get("net_salary", 0) for slip in sorted_slips]
            summary["trends"]["net_salary"] = {
                "values": net_values,
                "change": net_values[-1] - net_values[0],
                "change_pct": ((net_values[-1] - net_values[0]) / net_values[0]) * 100 if net_values[0] > 0 else 0
            }

            # מגמות ניכויים
            deduction_types = set()
            for slip in sorted_slips:
                deduction_types.update(slip.get("deductions", {}).keys())

            for deduction_type in deduction_types:
                values = [slip.get("deductions", {}).get(deduction_type, 0) for slip in sorted_slips]
                if any(values):
                    summary["trends"][f"deduction_{deduction_type}"] = {
                        "values": values,
                        "change": values[-1] - values[0] if values[0] is not None and values[-1] is not None else 0,
                        "change_pct": ((values[-1] - values[0]) / values[0]) * 100 if values[0] > 0 and values[-1] is not None else 0
                    }

        return summary

    def _create_merged_summary(self, merged_data: Dict[str, Any]) -> Dict[str, Any]:
        """יצירת סיכום כולל של הנתונים המאוחדים."""
        summary = {
            "financial_health": {},
            "asset_overview": {},
            "income_overview": {},
            "key_metrics": {}
        }

        # חישוב מצב פיננסי
        if "portfolio" in merged_data:
            portfolio = merged_data["portfolio"]

            if "summary" in portfolio:
                summary["asset_overview"]["total_portfolio_value"] = portfolio["summary"].get("total_value", 0)

            if "securities" in portfolio:
                summary["asset_overview"]["security_count"] = len(portfolio["securities"])

        if "balance_sheet" in merged_data:
            balance_sheet = merged_data["balance_sheet"]

            if "summary" in balance_sheet:
                summary["financial_health"]["total_assets"] = balance_sheet["summary"].get("total_assets", 0)
                summary["financial_health"]["total_liabilities"] = balance_sheet["summary"].get("total_liabilities", 0)
                summary["financial_health"]["total_equity"] = balance_sheet["summary"].get("total_equity", 0)

                # חישוב יחסים
                assets = balance_sheet["summary"].get("total_assets", 0)
                liabilities = balance_sheet["summary"].get("total_liabilities", 0)
                equity = balance_sheet["summary"].get("total_equity", 0)

                if assets > 0:
                    summary["key_metrics"]["debt_to_assets"] = liabilities / assets

                if equity > 0:
                    summary["key_metrics"]["debt_to_equity"] = liabilities / equity

        if "income_statement" in merged_data:
            income_statement = merged_data["income_statement"]

            if "summary" in income_statement:
                summary["income_overview"]["total_revenue"] = income_statement["summary"].get("total_revenue", 0)
                summary["income_overview"]["total_expenses"] = income_statement["summary"].get("total_expenses", 0)
                summary["income_overview"]["net_profit"] = income_statement["summary"].get("net_profit", 0)

                # חישוב שולי רווח
                revenue = income_statement["summary"].get("total_revenue", 0)
                net_profit = income_statement["summary"].get("net_profit", 0)

                if revenue > 0:
                    summary["key_metrics"]["profit_margin"] = (net_profit / revenue) * 100

        if "salary" in merged_data:
            salary = merged_data["salary"]

            if "summary" in salary:
                summary["income_overview"]["average_monthly_gross"] = salary["summary"].get("average_gross", 0)
                summary["income_overview"]["average_monthly_net"] = salary["summary"].get("average_net", 0)

        if "bank_statements" in merged_data:
            bank = merged_data["bank_statements"]

            if "summary" in bank:
                summary["financial_health"]["bank_balance"] = bank["summary"].get("end_balance", 0)
                summary["income_overview"]["monthly_credits"] = bank["summary"].get("total_credits", 0) / 12  # הנחה: נתוני שנה

        return summary