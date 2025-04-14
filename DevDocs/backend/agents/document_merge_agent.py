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
        comparison["summary"] = self._generate_comparison_summary(comparison["trends"])

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
            for _, value in row.items():
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
            for _, value in row.items():
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

    def _generate_comparison_summary(self, trends: Dict[str, Any]) -> Dict[str, Any]:
        """יצירת סיכום של שינויים משמעותיים בהתבסס על מגמות."""
        summary = {
            "significant_changes": []
        }

        # סיכום תיק השקעות
        if "portfolio" in trends and trends["portfolio"]:
            portfolio_trends = trends["portfolio"]

            # שינוי בשווי התיק
            if "value_change_pct" in portfolio_trends:
                change_pct = portfolio_trends["value_change_pct"]
                change = portfolio_trends["value_change"]

                if abs(change_pct) >= 5:  # שינוי של 5% נחשב משמעותי
                    direction = "עלה" if change > 0 else "ירד"
                    summary["portfolio"] = {
                        "portfolio_value_change": {
                            "type": "portfolio_value",
                            "change": change,
                            "change_pct": change_pct,
                            "description": f"שווי התיק {direction} ב-{abs(change_pct):.2f}% ({abs(change):.2f} יחידות)."
                        }
                    }

                    summary["significant_changes"].append({
                        "type": "portfolio_value",
                        "change_pct": change_pct,
                        "description": f"שווי התיק {direction} ב-{abs(change_pct):.2f}%."
                    })

        # סיכום מאזן
        if "balance_sheet" in trends and trends["balance_sheet"]:
            bs_trends = trends["balance_sheet"]

            # שינוי בנכסים
            if "assets_change_pct" in bs_trends:
                change_pct = bs_trends["assets_change_pct"]
                change = bs_trends["assets_change"]

                if abs(change_pct) >= 5:  # שינוי של 5% נחשב משמעותי
                    direction = "עלו" if change > 0 else "ירדו"
                    summary["financial_health"] = {
                        "assets_change": {
                            "type": "assets",
                            "change": change,
                            "change_pct": change_pct,
                            "description": f"סך הנכסים {direction} ב-{abs(change_pct):.2f}% ({abs(change):.2f} יחידות)."
                        }
                    }

                    summary["significant_changes"].append({
                        "type": "assets",
                        "change_pct": change_pct,
                        "description": f"סך הנכסים {direction} ב-{abs(change_pct):.2f}%."
                    })

            # שינוי בהתחייבויות
            if "liabilities_change_pct" in bs_trends:
                change_pct = bs_trends["liabilities_change_pct"]
                change = bs_trends["liabilities_change"]

                if abs(change_pct) >= 5:  # שינוי של 5% נחשב משמעותי
                    direction = "עלו" if change > 0 else "ירדו"
                    if "financial_health" not in summary:
                        summary["financial_health"] = {}

                    summary["financial_health"]["liabilities_change"] = {
                        "type": "liabilities",
                        "change": change,
                        "change_pct": change_pct,
                        "description": f"סך ההתחייבויות {direction} ב-{abs(change_pct):.2f}% ({abs(change):.2f} יחידות)."
                    }

                    summary["significant_changes"].append({
                        "type": "liabilities",
                        "change_pct": change_pct,
                        "description": f"סך ההתחייבויות {direction} ב-{abs(change_pct):.2f}%."
                    })

        # סיכום דוח רווח והפסד
        if "income_statement" in trends and trends["income_statement"]:
            is_trends = trends["income_statement"]

            # שינוי בהכנסות
            if "revenue_change_pct" in is_trends:
                change_pct = is_trends["revenue_change_pct"]
                change = is_trends["revenue_change"]

                if abs(change_pct) >= 5:  # שינוי של 5% נחשב משמעותי
                    direction = "עלו" if change > 0 else "ירדו"
                    summary["income"] = {
                        "revenue_change": {
                            "type": "revenue",
                            "change": change,
                            "change_pct": change_pct,
                            "description": f"סך ההכנסות {direction} ב-{abs(change_pct):.2f}% ({abs(change):.2f} יחידות)."
                        }
                    }

                    summary["significant_changes"].append({
                        "type": "revenue",
                        "change_pct": change_pct,
                        "description": f"סך ההכנסות {direction} ב-{abs(change_pct):.2f}%."
                    })

            # שינוי ברווח
            if "profit_change_pct" in is_trends:
                change_pct = is_trends["profit_change_pct"]
                change = is_trends["profit_change"]

                if abs(change_pct) >= 5:  # שינוי של 5% נחשב משמעותי
                    direction = "עלה" if change > 0 else "ירד"
                    if "income" not in summary:
                        summary["income"] = {}

                    summary["income"]["profit_change"] = {
                        "type": "profit",
                        "change": change,
                        "change_pct": change_pct,
                        "description": f"הרווח הנקי {direction} ב-{abs(change_pct):.2f}% ({abs(change):.2f} יחידות)."
                    }

                    summary["significant_changes"].append({
                        "type": "profit",
                        "change_pct": change_pct,
                        "description": f"הרווח הנקי {direction} ב-{abs(change_pct):.2f}%."
                    })

        # סיכום שכר
        if "salary" in trends and trends["salary"]:
            salary_trends = trends["salary"]

            # שינוי בשכר ברוטו
            if "gross_change_pct" in salary_trends:
                change_pct = salary_trends["gross_change_pct"]
                change = salary_trends["gross_change"]

                if abs(change_pct) >= 5:  # שינוי של 5% נחשב משמעותי
                    direction = "עלה" if change > 0 else "ירד"
                    summary["salary"] = {
                        "gross_change": {
                            "type": "gross_salary",
                            "change": change,
                            "change_pct": change_pct,
                            "description": f"השכר הברוטו הממוצע {direction} ב-{abs(change_pct):.2f}% ({abs(change):.2f} יחידות)."
                        }
                    }

                    summary["significant_changes"].append({
                        "type": "gross_salary",
                        "change_pct": change_pct,
                        "description": f"השכר הברוטו הממוצע {direction} ב-{abs(change_pct):.2f}%."
                    })

        return summary

    def _analyze_salary_trends(self, salary_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """ניתוח מגמות בנתוני שכר לאורך זמן."""
        if not salary_data_list or len(salary_data_list) < 2:
            return {}

        # סינון נתונים ריקים
        valid_data = [data for data in salary_data_list if data]
        if len(valid_data) < 2:
            return {}

        # קבלת הנתונים הישנים והחדשים ביותר
        oldest = valid_data[0]
        newest = valid_data[-1]

        # חישוב שינויים בשכר ברוטו ונטו
        oldest_gross = oldest.get("summary", {}).get("average_gross", 0)
        newest_gross = newest.get("summary", {}).get("average_gross", 0)

        gross_change = newest_gross - oldest_gross
        gross_change_pct = (gross_change / oldest_gross * 100) if oldest_gross > 0 else 0

        oldest_net = oldest.get("summary", {}).get("average_net", 0)
        newest_net = newest.get("summary", {}).get("average_net", 0)

        net_change = newest_net - oldest_net
        net_change_pct = (net_change / oldest_net * 100) if oldest_net > 0 else 0

        # חישוב שינויים בניכויים
        deduction_changes = []

        # איתור כל סוגי הניכויים הקיימים
        deduction_types = set()
        for data in valid_data:
            if "salary_slips" in data:
                for slip in data["salary_slips"]:
                    if "deductions" in slip:
                        deduction_types.update(slip["deductions"].keys())

        # חישוב ממוצעי ניכויים לכל סוג
        for deduction_type in deduction_types:
            oldest_avg = self._calculate_average_deduction(oldest, deduction_type)
            newest_avg = self._calculate_average_deduction(newest, deduction_type)

            if oldest_avg > 0 or newest_avg > 0:
                change = newest_avg - oldest_avg
                change_pct = (change / oldest_avg * 100) if oldest_avg > 0 else 0

                deduction_changes.append({
                    "type": deduction_type,
                    "old_value": oldest_avg,
                    "new_value": newest_avg,
                    "change": change,
                    "change_pct": change_pct
                })

        # מיון לפי אחוז שינוי מוחלט
        deduction_changes.sort(key=lambda x: abs(x["change_pct"]), reverse=True)

        return {
            "gross_change": gross_change,
            "gross_change_pct": gross_change_pct,
            "net_change": net_change,
            "net_change_pct": net_change_pct,
            "deduction_changes": deduction_changes[:5]  # 5 השינויים המשמעותיים ביותר
        }

    def _calculate_average_deduction(self, salary_data: Dict[str, Any], deduction_type: str) -> float:
        """חישוב ממוצע ניכוי מסוג מסוים בכל תלושי השכר."""
        if "salary_slips" not in salary_data or not salary_data["salary_slips"]:
            return 0.0

        total = 0.0
        count = 0

        for slip in salary_data["salary_slips"]:
            if "deductions" in slip and deduction_type in slip["deductions"]:
                total += slip["deductions"][deduction_type]
                count += 1

        return total / count if count > 0 else 0.0

    def _analyze_income_statement_trends(self, income_statement_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """ניתוח מגמות בדוח רווח והפסד לאורך זמן."""
        if not income_statement_data_list or len(income_statement_data_list) < 2:
            return {}

        # סינון נתונים ריקים
        valid_data = [data for data in income_statement_data_list if data]
        if len(valid_data) < 2:
            return {}

        # קבלת הנתונים הישנים והחדשים ביותר
        oldest = valid_data[0]
        newest = valid_data[-1]

        # חישוב שינויים בהכנסות, הוצאות ורווח
        oldest_revenue = oldest.get("summary", {}).get("total_revenue", 0)
        newest_revenue = newest.get("summary", {}).get("total_revenue", 0)

        revenue_change = newest_revenue - oldest_revenue
        revenue_change_pct = (revenue_change / oldest_revenue * 100) if oldest_revenue > 0 else 0

        oldest_expenses = oldest.get("summary", {}).get("total_expenses", 0)
        newest_expenses = newest.get("summary", {}).get("total_expenses", 0)

        expenses_change = newest_expenses - oldest_expenses
        expenses_change_pct = (expenses_change / oldest_expenses * 100) if oldest_expenses > 0 else 0

        oldest_profit = oldest.get("summary", {}).get("net_profit", 0)
        newest_profit = newest.get("summary", {}).get("net_profit", 0)

        profit_change = newest_profit - oldest_profit
        profit_change_pct = (profit_change / oldest_profit * 100) if oldest_profit > 0 else 0

        # זיהוי שינויים משמעותיים בקטגוריות הכנסה או הוצאה ספציפיות
        major_changes = []

        # בדיקת הכנסות
        for revenue_name, revenue_value in newest.get("revenues", {}).items():
            if revenue_name in oldest.get("revenues", {}):
                old_value = oldest["revenues"][revenue_name]
                change = revenue_value - old_value
                change_pct = (change / old_value * 100) if old_value > 0 else 0

                if abs(change_pct) >= 10:  # שינוי של 10% נחשב משמעותי
                    major_changes.append({
                        "name": revenue_name,
                        "type": "revenue",
                        "old_value": old_value,
                        "new_value": revenue_value,
                        "change": change,
                        "change_pct": change_pct
                    })

        # בדיקת הוצאות
        for expense_name, expense_value in newest.get("expenses", {}).items():
            if expense_name in oldest.get("expenses", {}):
                old_value = oldest["expenses"][expense_name]
                change = expense_value - old_value
                change_pct = (change / old_value * 100) if old_value > 0 else 0

                if abs(change_pct) >= 10:  # שינוי של 10% נחשב משמעותי
                    major_changes.append({
                        "name": expense_name,
                        "type": "expense",
                        "old_value": old_value,
                        "new_value": expense_value,
                        "change": change,
                        "change_pct": change_pct
                    })

        # מיון לפי אחוז שינוי מוחלט
        major_changes.sort(key=lambda x: abs(x["change_pct"]), reverse=True)

        return {
            "revenue_change": revenue_change,
            "revenue_change_pct": revenue_change_pct,
            "expenses_change": expenses_change,
            "expenses_change_pct": expenses_change_pct,
            "profit_change": profit_change,
            "profit_change_pct": profit_change_pct,
            "major_changes": major_changes[:5]  # 5 השינויים המשמעותיים ביותר
        }

    def _analyze_balance_sheet_trends(self, balance_sheet_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """ניתוח מגמות במאזן לאורך זמן."""
        if not balance_sheet_data_list or len(balance_sheet_data_list) < 2:
            return {}

        # סינון נתונים ריקים
        valid_data = [data for data in balance_sheet_data_list if data]
        if len(valid_data) < 2:
            return {}

        # קבלת הנתונים הישנים והחדשים ביותר
        oldest = valid_data[0]
        newest = valid_data[-1]

        # חישוב שינויים בנכסים, התחייבויות והון
        oldest_assets = oldest.get("summary", {}).get("total_assets", 0)
        newest_assets = newest.get("summary", {}).get("total_assets", 0)

        assets_change = newest_assets - oldest_assets
        assets_change_pct = (assets_change / oldest_assets * 100) if oldest_assets > 0 else 0

        oldest_liabilities = oldest.get("summary", {}).get("total_liabilities", 0)
        newest_liabilities = newest.get("summary", {}).get("total_liabilities", 0)

        liabilities_change = newest_liabilities - oldest_liabilities
        liabilities_change_pct = (liabilities_change / oldest_liabilities * 100) if oldest_liabilities > 0 else 0

        oldest_equity = oldest.get("summary", {}).get("total_equity", 0)
        newest_equity = newest.get("summary", {}).get("total_equity", 0)

        equity_change = newest_equity - oldest_equity
        equity_change_pct = (equity_change / oldest_equity * 100) if oldest_equity > 0 else 0

        # זיהוי שינויים משמעותיים בנכסים או התחייבויות ספציפיים
        major_changes = []

        # בדיקת נכסים
        for asset_name, asset_value in newest.get("assets", {}).items():
            if asset_name in oldest.get("assets", {}):
                old_value = oldest["assets"][asset_name]
                change = asset_value - old_value
                change_pct = (change / old_value * 100) if old_value > 0 else 0

                if abs(change_pct) >= 10:  # שינוי של 10% נחשב משמעותי
                    major_changes.append({
                        "name": asset_name,
                        "type": "asset",
                        "old_value": old_value,
                        "new_value": asset_value,
                        "change": change,
                        "change_pct": change_pct
                    })

        # בדיקת התחייבויות
        for liability_name, liability_value in newest.get("liabilities", {}).items():
            if liability_name in oldest.get("liabilities", {}):
                old_value = oldest["liabilities"][liability_name]
                change = liability_value - old_value
                change_pct = (change / old_value * 100) if old_value > 0 else 0

                if abs(change_pct) >= 10:  # שינוי של 10% נחשב משמעותי
                    major_changes.append({
                        "name": liability_name,
                        "type": "liability",
                        "old_value": old_value,
                        "new_value": liability_value,
                        "change": change,
                        "change_pct": change_pct
                    })

        # מיון לפי אחוז שינוי מוחלט
        major_changes.sort(key=lambda x: abs(x["change_pct"]), reverse=True)

        return {
            "assets_change": assets_change,
            "assets_change_pct": assets_change_pct,
            "liabilities_change": liabilities_change,
            "liabilities_change_pct": liabilities_change_pct,
            "equity_change": equity_change,
            "equity_change_pct": equity_change_pct,
            "major_changes": major_changes[:5]  # 5 השינויים המשמעותיים ביותר
        }

    def _analyze_portfolio_trends(self, portfolio_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """ניתוח מגמות בתיק השקעות לאורך זמן."""
        if not portfolio_data_list or len(portfolio_data_list) < 2:
            return {}

        # סינון נתונים ריקים
        valid_data = [data for data in portfolio_data_list if data]
        if len(valid_data) < 2:
            return {}

        # קבלת הנתונים הישנים והחדשים ביותר
        oldest = valid_data[0]
        newest = valid_data[-1]

        # חישוב שינוי בשווי התיק
        oldest_value = oldest.get("summary", {}).get("total_value", 0)
        newest_value = newest.get("summary", {}).get("total_value", 0)

        value_change = newest_value - oldest_value
        value_change_pct = (value_change / oldest_value * 100) if oldest_value > 0 else 0

        # זיהוי הניירות המובילים
        top_performers = []
        if newest.get("securities"):
            securities = newest["securities"]
            # מיון לפי תשואה
            sorted_securities = sorted(securities, key=lambda x: x.get("return", 0), reverse=True)
            # לקיחת ה-5 המובילים
            top_performers = sorted_securities[:min(5, len(sorted_securities))]

            # הוספת נתוני תשואה ממוצעת
            for security in top_performers:
                # חיפוש הנייר בנתונים ישנים לחישוב תשואה ממוצעת
                security_name = security.get("name", "")
                security_isin = security.get("isin", "")

                historical_returns = []
                for data in valid_data:
                    if data.get("securities"):
                        for old_security in data["securities"]:
                            if (old_security.get("name") == security_name or
                                old_security.get("isin") == security_isin):
                                if "return" in old_security:
                                    historical_returns.append(old_security["return"])
                                break

                if historical_returns:
                    security["average_return"] = sum(historical_returns) / len(historical_returns)
                else:
                    security["average_return"] = security.get("return", 0)

        return {
            "value_change": value_change,
            "value_change_pct": value_change_pct,
            "top_performers": top_performers
        }

    def _analyze_income_and_expenses(self, merged_data: Dict[str, Any]) -> Dict[str, Any]:
        """ניתוח הכנסות והוצאות מהנתונים המאוחדים."""
        analysis = {
            "total_income": 0,
            "total_expenses": 0,
            "net_income": 0,
            "income_breakdown": [],
            "expense_breakdown": [],
            "monthly_cash_flow": 0,
            "recommendations": []
        }

        # חילוץ נתוני דוח רווח והפסד
        if "income_statement" in merged_data:
            income_statement = merged_data["income_statement"]

            if "summary" in income_statement:
                analysis["total_income"] = income_statement["summary"].get("total_revenue", 0)
                analysis["total_expenses"] = income_statement["summary"].get("total_expenses", 0)
                analysis["net_income"] = income_statement["summary"].get("net_profit", 0)
                analysis["monthly_cash_flow"] = analysis["net_income"] / 12  # הנחה: נתונים שנתיים

            # פירוט הכנסות
            if "revenues" in income_statement:
                for income_name, income_value in income_statement["revenues"].items():
                    analysis["income_breakdown"].append({
                        "name": income_name,
                        "value": income_value,
                        "percentage": (income_value / analysis["total_income"] * 100) if analysis["total_income"] > 0 else 0
                    })

                # מיון לפי ערך
                analysis["income_breakdown"].sort(key=lambda x: x["value"], reverse=True)

            # פירוט הוצאות
            if "expenses" in income_statement:
                for expense_name, expense_value in income_statement["expenses"].items():
                    analysis["expense_breakdown"].append({
                        "name": expense_name,
                        "value": expense_value,
                        "percentage": (expense_value / analysis["total_expenses"] * 100) if analysis["total_expenses"] > 0 else 0
                    })

                # מיון לפי ערך
                analysis["expense_breakdown"].sort(key=lambda x: x["value"], reverse=True)

        # אם אין נתוני דוח רווח והפסד, השתמש בנתוני שכר
        if analysis["total_income"] == 0 and "salary" in merged_data:
            salary_data = merged_data["salary"]

            if "summary" in salary_data:
                analysis["total_income"] = salary_data["summary"].get("average_gross", 0) * 12  # שנתי

                # הוספת שכר לפירוט הכנסות
                analysis["income_breakdown"].append({
                    "name": "שכר עבודה",
                    "value": analysis["total_income"],
                    "percentage": 100
                })

        # אם אין נתוני הוצאות, השתמש בנתוני בנק
        if analysis["total_expenses"] == 0 and "bank_statements" in merged_data:
            bank_data = merged_data["bank_statements"]

            if "summary" in bank_data:
                analysis["total_expenses"] = bank_data["summary"].get("total_debits", 0)  # הנחה: נתונים שנתיים

                # חישוב הכנסה נטו
                analysis["net_income"] = analysis["total_income"] - analysis["total_expenses"]
                analysis["monthly_cash_flow"] = analysis["net_income"] / 12

                # הוספת הוצאות כלליות לפירוט הוצאות
                analysis["expense_breakdown"].append({
                    "name": "הוצאות כלליות",
                    "value": analysis["total_expenses"],
                    "percentage": 100
                })

        # המלצות
        # תזרים מזומנים שלילי
        if analysis["monthly_cash_flow"] < 0:
            analysis["recommendations"].append({
                "title": "תזרים מזומנים שלילי",
                "description": f"ההוצאות שלך גבוהות מההכנסות ב-{abs(analysis['monthly_cash_flow']):.2f} לחודש.",
                "action": "שקול להפחית הוצאות או להגדיל הכנסות כדי להימנע מהצטברות חובות.",
                "priority": "high"
            })

        # ריכוז גבוה של הוצאות
        if analysis["expense_breakdown"] and analysis["expense_breakdown"][0]["percentage"] > 50:
            analysis["recommendations"].append({
                "title": "ריכוז גבוה של הוצאות",
                "description": f"{analysis['expense_breakdown'][0]['name']} מהווה {analysis['expense_breakdown'][0]['percentage']:.2f}% מסך ההוצאות שלך.",
                "action": "בדוק אפשרויות להפחתת הוצאה זו או לאזן את התקציב שלך.",
                "priority": "medium"
            })

        return analysis

    def _generate_comprehensive_recommendations(self, report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """יצירת המלצות מקיפות בהתבסס על כל הנתונים המנותחים."""
        all_recommendations = []

        # איסוף המלצות מכל הניתוחים
        if "assets_and_liabilities" in report and "recommendations" in report["assets_and_liabilities"]:
            all_recommendations.extend(report["assets_and_liabilities"]["recommendations"])

        if "income_and_expenses" in report and "recommendations" in report["income_and_expenses"]:
            all_recommendations.extend(report["income_and_expenses"]["recommendations"])

        if "investments" in report and "recommendations" in report["investments"]:
            all_recommendations.extend(report["investments"]["recommendations"])

        # הוספת המלצות משולבות בהתבסס על נתונים משולבים

        # בדיקת יחס הוצאות להכנסות
        if "income_and_expenses" in report:
            income_data = report["income_and_expenses"]
            total_income = income_data.get("total_income", 0)
            total_expenses = income_data.get("total_expenses", 0)

            if total_income > 0 and total_expenses / total_income > 0.9:
                all_recommendations.append({
                    "title": "יחס הוצאות להכנסות גבוה",
                    "description": f"ההוצאות שלך מהוות {(total_expenses / total_income * 100):.2f}% מההכנסות שלך.",
                    "action": "שקול להגדיל את שיעור החיסכון שלך על ידי הפחתת הוצאות או הגדלת הכנסות.",
                    "priority": "medium"
                })

        # בדיקת יחס נכסים נזילים
        if "assets_and_liabilities" in report and "financial_snapshot" in report:
            assets_data = report["assets_and_liabilities"]
            snapshot = report["financial_snapshot"]

            # חישוב נכסים נזילים
            monthly_expenses = snapshot.get("monthly_expenses", 0) * 6  # 6 חודשי הוצאות

            # בדיקה אם יש מספיק נכסים נזילים
            liquid_assets = 0
            for asset in assets_data.get("asset_breakdown", []):
                if asset["name"].lower() in ["cash", "cash and cash equivalents", "מזומנים", "שווי מזומנים"]:
                    liquid_assets += asset["value"]

            if monthly_expenses > 0 and liquid_assets < monthly_expenses:
                all_recommendations.append({
                    "title": "רמת נזילות נמוכה",
                    "description": f"הנכסים הנזילים שלך ({liquid_assets:.2f}) נמוכים מהוצאות ל-6 חודשים ({monthly_expenses:.2f}).",
                    "action": "שקול להגדיל את קרן החירום שלך לכיסוי 6 חודשי הוצאות לפחות.",
                    "priority": "high"
                })

        # בדיקת איזון תיק השקעות ביחס לגיל
        if "investments" in report and "financial_snapshot" in report:
            # הוספת המלצות נוספות בהתאם לנתונים הקיימים
            pass

        # מיון המלצות לפי עדיפות
        priority_order = {"high": 0, "medium": 1, "low": 2}
        all_recommendations.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 3))

        return all_recommendations

    def _analyze_investments(self, merged_data: Dict[str, Any]) -> Dict[str, Any]:
        """ניתוח השקעות מהנתונים המאוחדים."""
        analysis = {
            "total_portfolio_value": 0,
            "asset_allocation": [],
            "top_performers": [],
            "historical_performance": {},
            "recommendations": []
        }

        # חילוץ נתוני תיק השקעות
        if "portfolio" in merged_data:
            portfolio = merged_data["portfolio"]

            if "summary" in portfolio:
                analysis["total_portfolio_value"] = portfolio["summary"].get("total_value", 0)

            # פירוט ניירות ערך
            if "securities" in portfolio:
                # חלוקה לפי סוגי נכסים
                asset_types = {}

                for security in portfolio["securities"]:
                    security_type = security.get("type", "אחר")
                    security_value = security.get("value", 0)

                    if security_type not in asset_types:
                        asset_types[security_type] = 0

                    asset_types[security_type] += security_value

                # יצירת הקצאת נכסים
                for asset_type, value in asset_types.items():
                    analysis["asset_allocation"].append({
                        "type": asset_type,
                        "value": value,
                        "percentage": (value / analysis["total_portfolio_value"] * 100) if analysis["total_portfolio_value"] > 0 else 0
                    })

                # מיון לפי ערך
                analysis["asset_allocation"].sort(key=lambda x: x["value"], reverse=True)

                # זיהוי המובילים
                top_performers = sorted(portfolio["securities"], key=lambda x: x.get("return", 0), reverse=True)
                analysis["top_performers"] = top_performers[:min(5, len(top_performers))]

            # נתונים היסטוריים
            if "historical_data" in portfolio and "portfolio_values" in portfolio["historical_data"]:
                analysis["historical_performance"] = {
                    "values": portfolio["historical_data"]["portfolio_values"],
                    "returns": portfolio["historical_data"].get("returns", [])
                }

        # המלצות
        # איזון תיק
        if len(analysis["asset_allocation"]) > 0 and analysis["asset_allocation"][0]["percentage"] > 70:
            analysis["recommendations"].append({
                "title": "תיק לא מאוזן",
                "description": f"{analysis['asset_allocation'][0]['type']} מהווה {analysis['asset_allocation'][0]['percentage']:.2f}% מתיק ההשקעות שלך.",
                "action": "שקול לגוון את התיק על ידי השקעה בסוגי נכסים נוספים.",
                "priority": "medium"
            })

        return analysis

    def _analyze_assets_and_liabilities(self, merged_data: Dict[str, Any]) -> Dict[str, Any]:
        """ניתוח נכסים והתחייבויות מהנתונים המאוחדים."""
        analysis = {
            "total_assets": 0,
            "total_liabilities": 0,
            "net_worth": 0,
            "debt_to_equity_ratio": 0,
            "asset_breakdown": [],
            "liability_breakdown": [],
            "recommendations": []
        }

        # חילוץ נתוני מאזן
        if "balance_sheet" in merged_data:
            balance_sheet = merged_data["balance_sheet"]

            if "summary" in balance_sheet:
                analysis["total_assets"] = balance_sheet["summary"].get("total_assets", 0)
                analysis["total_liabilities"] = balance_sheet["summary"].get("total_liabilities", 0)
                analysis["net_worth"] = balance_sheet["summary"].get("total_equity", 0)

                # חישוב יחס חוב להון
                if analysis["net_worth"] > 0:
                    analysis["debt_to_equity_ratio"] = analysis["total_liabilities"] / analysis["net_worth"]

            # פירוט נכסים
            if "assets" in balance_sheet:
                for asset_name, asset_value in balance_sheet["assets"].items():
                    analysis["asset_breakdown"].append({
                        "name": asset_name,
                        "value": asset_value,
                        "percentage": (asset_value / analysis["total_assets"] * 100) if analysis["total_assets"] > 0 else 0
                    })

                # מיון לפי ערך
                analysis["asset_breakdown"].sort(key=lambda x: x["value"], reverse=True)

            # פירוט התחייבויות
            if "liabilities" in balance_sheet:
                for liability_name, liability_value in balance_sheet["liabilities"].items():
                    analysis["liability_breakdown"].append({
                        "name": liability_name,
                        "value": liability_value,
                        "percentage": (liability_value / analysis["total_liabilities"] * 100) if analysis["total_liabilities"] > 0 else 0
                    })

                # מיון לפי ערך
                analysis["liability_breakdown"].sort(key=lambda x: x["value"], reverse=True)

        # הוספת נתוני תיק השקעות
        if "portfolio" in merged_data and "summary" in merged_data["portfolio"]:
            portfolio_value = merged_data["portfolio"]["summary"].get("total_value", 0)

            # הוספת תיק השקעות לנכסים
            if portfolio_value > 0:
                analysis["asset_breakdown"].append({
                    "name": "תיק השקעות",
                    "value": portfolio_value,
                    "percentage": (portfolio_value / analysis["total_assets"] * 100) if analysis["total_assets"] > 0 else 0
                })

                # מיון מחדש
                analysis["asset_breakdown"].sort(key=lambda x: x["value"], reverse=True)

        # המלצות
        # יחס חוב להון גבוה
        if analysis["debt_to_equity_ratio"] > 0.8:
            analysis["recommendations"].append({
                "title": "יחס חוב להון גבוה",
                "description": f"יחס החוב להון שלך עומד על {analysis['debt_to_equity_ratio']:.2f}, אשר נחשב גבוה.",
                "action": "שקול להפחית את רמת החוב או להגדיל את ההון העצמי שלך.",
                "priority": "high"
            })

        # ריכוז גבוה של נכסים
        if analysis["asset_breakdown"] and analysis["asset_breakdown"][0]["percentage"] > 70:
            analysis["recommendations"].append({
                "title": "ריכוז גבוה של נכסים",
                "description": f"{analysis['asset_breakdown'][0]['name']} מהווה {analysis['asset_breakdown'][0]['percentage']:.2f}% מסך הנכסים שלך.",
                "action": "שקול לגוון את הנכסים שלך להפחתת סיכונים.",
                "priority": "medium"
            })

        return analysis

    def _create_financial_snapshot(self, merged_data: Dict[str, Any]) -> Dict[str, Any]:
        """יצירת תמונת מצב פיננסית עדכנית מהנתונים המאוחדים."""
        snapshot = {
            "total_assets": 0,
            "total_liabilities": 0,
            "net_worth": 0,
            "monthly_income": 0,
            "monthly_expenses": 0,
            "portfolio_value": 0,
            "debt_to_equity_ratio": 0,
            "profit_margin": 0
        }

        # נכסים והתחייבויות
        if "balance_sheet" in merged_data:
            balance_sheet = merged_data["balance_sheet"]

            if "summary" in balance_sheet:
                snapshot["total_assets"] = balance_sheet["summary"].get("total_assets", 0)
                snapshot["total_liabilities"] = balance_sheet["summary"].get("total_liabilities", 0)
                snapshot["net_worth"] = balance_sheet["summary"].get("total_equity", 0)

                # חישוב יחס חוב להון
                if snapshot["net_worth"] > 0:
                    snapshot["debt_to_equity_ratio"] = snapshot["total_liabilities"] / snapshot["net_worth"]

        # שווי תיק
        if "portfolio" in merged_data and "summary" in merged_data["portfolio"]:
            snapshot["portfolio_value"] = merged_data["portfolio"]["summary"].get("total_value", 0)

        # הכנסה והוצאות
        if "income_statement" in merged_data and "summary" in merged_data["income_statement"]:
            income_summary = merged_data["income_statement"]["summary"]

            # הנחה: הנתונים הם שנתיים, חלוקה ב-12 לקבלת נתונים חודשיים
            snapshot["monthly_income"] = income_summary.get("total_revenue", 0) / 12
            snapshot["monthly_expenses"] = income_summary.get("total_expenses", 0) / 12

            # חישוב שולי רווח
            if income_summary.get("total_revenue", 0) > 0:
                snapshot["profit_margin"] = (income_summary.get("net_profit", 0) / income_summary.get("total_revenue", 0)) * 100

        # שכר
        if "salary" in merged_data and "summary" in merged_data["salary"]:
            salary_summary = merged_data["salary"]["summary"]

            # אם אין נתוני הכנסה מדוח רווח והפסד, השתמש בנתוני שכר
            if snapshot["monthly_income"] == 0:
                snapshot["monthly_income"] = salary_summary.get("average_gross", 0)

        # בנק
        if "bank_statements" in merged_data and "summary" in merged_data["bank_statements"]:
            bank_summary = merged_data["bank_statements"]["summary"]

            # אם אין נתוני הוצאות מדוח רווח והפסד, השתמש בנתוני בנק
            if snapshot["monthly_expenses"] == 0:
                # הנחה: הנתונים הם שנתיים, חלוקה ב-12 לקבלת נתונים חודשיים
                snapshot["monthly_expenses"] = bank_summary.get("total_debits", 0) / 12

        return snapshot

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