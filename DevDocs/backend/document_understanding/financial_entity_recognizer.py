import re
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
import pandas as pd
import numpy as np
from datetime import datetime
import spacy
from spacy.matcher import Matcher, PhraseMatcher
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinancialEntityRecognizer:
    """
    Financial Entity Recognizer for extracting financial entities from text and tables.
    """
    
    def __init__(self, load_spacy_model: bool = True):
        """
        Initialize the Financial Entity Recognizer.
        
        Args:
            load_spacy_model: Whether to load the spaCy model
        """
        self.spacy_model = None
        
        if load_spacy_model:
            try:
                # Load spaCy model
                self.spacy_model = spacy.load("en_core_web_sm")
                logger.info("Loaded spaCy model")
            except Exception as e:
                logger.warning(f"Could not load spaCy model: {e}")
        
        # Initialize matchers
        self._initialize_matchers()
        
        # Load financial terms and patterns
        self._load_financial_terms()
    
    def _initialize_matchers(self):
        """Initialize pattern matchers for financial entities."""
        if self.spacy_model:
            # Create matchers
            self.matcher = Matcher(self.spacy_model.vocab)
            self.phrase_matcher = PhraseMatcher(self.spacy_model.vocab)
            
            # Add patterns for financial entities
            self._add_currency_patterns()
            self._add_percentage_patterns()
            self._add_date_patterns()
            self._add_number_patterns()
    
    def _add_currency_patterns(self):
        """Add patterns for currency recognition."""
        if not self.spacy_model:
            return
        
        # Currency symbols followed by numbers
        self.matcher.add("CURRENCY", [
            [{"TEXT": {"REGEX": r"[$€£¥]"}}, {"IS_DIGIT": True}],
            [{"TEXT": {"REGEX": r"[$€£¥]"}}, {"IS_DIGIT": True}, {"TEXT": "."}, {"IS_DIGIT": True}],
            [{"TEXT": {"REGEX": r"[$€£¥]"}}, {"TEXT": {"REGEX": r"\d+,\d+"}}],
            [{"IS_DIGIT": True}, {"LOWER": {"IN": ["usd", "eur", "gbp", "jpy", "dollars", "euros", "pounds"]}}],
            [{"TEXT": {"REGEX": r"\d+\.\d+"}}, {"LOWER": {"IN": ["usd", "eur", "gbp", "jpy", "dollars", "euros", "pounds"]}}],
        ])
    
    def _add_percentage_patterns(self):
        """Add patterns for percentage recognition."""
        if not self.spacy_model:
            return
        
        # Percentage patterns
        self.matcher.add("PERCENTAGE", [
            [{"IS_DIGIT": True}, {"TEXT": "%"}],
            [{"TEXT": {"REGEX": r"\d+\.\d+"}}, {"TEXT": "%"}],
            [{"IS_DIGIT": True}, {"LOWER": "percent"}],
            [{"TEXT": {"REGEX": r"\d+\.\d+"}}, {"LOWER": "percent"}],
            [{"IS_DIGIT": True}, {"LOWER": "percentage"}],
            [{"TEXT": {"REGEX": r"\d+\.\d+"}}, {"LOWER": "percentage"}],
        ])
    
    def _add_date_patterns(self):
        """Add patterns for date recognition."""
        if not self.spacy_model:
            return
        
        # Date patterns
        self.matcher.add("DATE", [
            # MM/DD/YYYY or DD/MM/YYYY
            [{"TEXT": {"REGEX": r"\d{1,2}/\d{1,2}/\d{2,4}"}}],
            # YYYY-MM-DD
            [{"TEXT": {"REGEX": r"\d{4}-\d{1,2}-\d{1,2}"}}],
            # Month DD, YYYY
            [{"IS_TITLE": True, "POS": "PROPN"}, {"IS_DIGIT": True}, {"TEXT": ","}, {"IS_DIGIT": True, "LENGTH": 4}],
            # Quarter patterns
            [{"TEXT": {"REGEX": r"Q[1-4]"}}, {"IS_DIGIT": True, "LENGTH": 4}],
            [{"LOWER": {"IN": ["first", "second", "third", "fourth"]}}, {"LOWER": "quarter"}, {"IS_DIGIT": True, "LENGTH": 4}],
            # Fiscal year
            [{"LOWER": "fy"}, {"IS_DIGIT": True}],
            [{"LOWER": "fiscal"}, {"LOWER": "year"}, {"IS_DIGIT": True}],
        ])
    
    def _add_number_patterns(self):
        """Add patterns for number recognition."""
        if not self.spacy_model:
            return
        
        # Number patterns
        self.matcher.add("NUMBER", [
            # Large numbers with commas
            [{"TEXT": {"REGEX": r"\d{1,3}(,\d{3})+"}}],
            # Numbers with decimals
            [{"TEXT": {"REGEX": r"\d+\.\d+"}}],
            # Numbers with K, M, B, T suffixes
            [{"IS_DIGIT": True}, {"LOWER": {"IN": ["k", "m", "b", "t"]}}],
            [{"TEXT": {"REGEX": r"\d+\.\d+"}}, {"LOWER": {"IN": ["k", "m", "b", "t"]}}],
            # Numbers with thousand, million, billion, trillion
            [{"IS_DIGIT": True}, {"LOWER": {"IN": ["thousand", "million", "billion", "trillion"]}}],
            [{"TEXT": {"REGEX": r"\d+\.\d+"}}, {"LOWER": {"IN": ["thousand", "million", "billion", "trillion"]}}],
        ])
    
    def _load_financial_terms(self):
        """Load financial terms and metrics."""
        # Common financial metrics
        self.financial_metrics = {
            "income_statement": [
                "revenue", "sales", "income", "gross profit", "operating income", "ebitda", 
                "net income", "earnings per share", "eps", "cost of goods sold", "cogs",
                "operating expenses", "opex", "interest expense", "tax expense", "depreciation",
                "amortization", "r&d", "research and development"
            ],
            "balance_sheet": [
                "assets", "total assets", "current assets", "non-current assets", "liabilities",
                "total liabilities", "current liabilities", "non-current liabilities", "equity",
                "shareholders equity", "cash", "cash equivalents", "accounts receivable", "inventory",
                "property plant and equipment", "ppe", "goodwill", "intangible assets", "debt",
                "long-term debt", "short-term debt", "accounts payable", "retained earnings"
            ],
            "cash_flow": [
                "cash flow", "operating cash flow", "investing cash flow", "financing cash flow",
                "free cash flow", "fcf", "capital expenditures", "capex", "dividends paid",
                "share repurchases", "stock buybacks"
            ],
            "ratios": [
                "p/e ratio", "price to earnings", "p/b ratio", "price to book", "p/s ratio",
                "price to sales", "ev/ebitda", "roe", "return on equity", "roa", "return on assets",
                "roi", "return on investment", "gross margin", "operating margin", "profit margin",
                "net margin", "debt to equity", "current ratio", "quick ratio", "dividend yield",
                "payout ratio", "beta"
            ]
        }
        
        # Add financial metrics to phrase matcher
        if self.spacy_model:
            for category, terms in self.financial_metrics.items():
                patterns = [self.spacy_model.make_doc(term) for term in terms]
                self.phrase_matcher.add(category.upper(), None, *patterns)
    
    def extract_entities(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract financial entities from text.
        
        Args:
            text: Text to extract entities from
            
        Returns:
            Dictionary of extracted entities by type
        """
        if not self.spacy_model:
            return self._extract_entities_with_regex(text)
        
        # Process text with spaCy
        doc = self.spacy_model(text)
        
        # Extract entities using matchers
        matches = self.matcher(doc)
        phrase_matches = self.phrase_matcher(doc)
        
        # Organize entities by type
        entities = {
            "currencies": [],
            "percentages": [],
            "dates": [],
            "numbers": [],
            "financial_metrics": [],
            "organizations": [],
            "named_entities": []
        }
        
        # Process matcher results
        for match_id, start, end in matches:
            span = doc[start:end]
            match_type = self.spacy_model.vocab.strings[match_id]
            
            entity = {
                "text": span.text,
                "start": span.start_char,
                "end": span.end_char,
                "value": self._normalize_entity_value(span.text, match_type)
            }
            
            if match_type == "CURRENCY":
                entities["currencies"].append(entity)
            elif match_type == "PERCENTAGE":
                entities["percentages"].append(entity)
            elif match_type == "DATE":
                entities["dates"].append(entity)
            elif match_type == "NUMBER":
                entities["numbers"].append(entity)
        
        # Process phrase matcher results
        for match_id, start, end in phrase_matches:
            span = doc[start:end]
            match_type = self.spacy_model.vocab.strings[match_id]
            
            entity = {
                "text": span.text,
                "start": span.start_char,
                "end": span.end_char,
                "category": match_type.lower()
            }
            
            entities["financial_metrics"].append(entity)
        
        # Extract named entities from spaCy
        for ent in doc.ents:
            if ent.label_ == "ORG":
                entities["organizations"].append({
                    "text": ent.text,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "label": ent.label_
                })
            else:
                entities["named_entities"].append({
                    "text": ent.text,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "label": ent.label_
                })
        
        return entities
    
    def _extract_entities_with_regex(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract financial entities using regex patterns (fallback if spaCy is not available).
        
        Args:
            text: Text to extract entities from
            
        Returns:
            Dictionary of extracted entities by type
        """
        entities = {
            "currencies": [],
            "percentages": [],
            "dates": [],
            "numbers": [],
            "financial_metrics": [],
            "organizations": [],
            "named_entities": []
        }
        
        # Currency regex
        currency_pattern = r'[$€£¥](\d{1,3}(,\d{3})+|\d+(\.\d+)?)'
        for match in re.finditer(currency_pattern, text):
            entities["currencies"].append({
                "text": match.group(0),
                "start": match.start(),
                "end": match.end(),
                "value": self._normalize_entity_value(match.group(0), "CURRENCY")
            })
        
        # Percentage regex
        percentage_pattern = r'(\d+(\.\d+)?)\s*%'
        for match in re.finditer(percentage_pattern, text):
            entities["percentages"].append({
                "text": match.group(0),
                "start": match.start(),
                "end": match.end(),
                "value": self._normalize_entity_value(match.group(0), "PERCENTAGE")
            })
        
        # Date regex
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',  # MM/DD/YYYY or DD/MM/YYYY
            r'\d{4}-\d{1,2}-\d{1,2}',    # YYYY-MM-DD
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}',  # Month DD, YYYY
            r'Q[1-4]\s+\d{4}',           # Q1 2023
            r'FY\s*\d{4}'                # FY2023
        ]
        
        for pattern in date_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities["dates"].append({
                    "text": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "value": self._normalize_entity_value(match.group(0), "DATE")
                })
        
        # Number regex
        number_patterns = [
            r'\d{1,3}(,\d{3})+',  # Numbers with commas
            r'\d+\.\d+',          # Numbers with decimals
            r'\d+\s*(k|m|b|t)',   # Numbers with K, M, B, T suffixes
            r'\d+(\.\d+)?\s*(thousand|million|billion|trillion)'  # Numbers with thousand, million, etc.
        ]
        
        for pattern in number_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities["numbers"].append({
                    "text": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "value": self._normalize_entity_value(match.group(0), "NUMBER")
                })
        
        # Financial metrics
        for category, terms in self.financial_metrics.items():
            for term in terms:
                for match in re.finditer(r'\b' + re.escape(term) + r'\b', text, re.IGNORECASE):
                    entities["financial_metrics"].append({
                        "text": match.group(0),
                        "start": match.start(),
                        "end": match.end(),
                        "category": category
                    })
        
        return entities
    
    def _normalize_entity_value(self, text: str, entity_type: str) -> Any:
        """
        Normalize entity values (e.g., convert "$1,000" to 1000.0).
        
        Args:
            text: Entity text
            entity_type: Type of entity
            
        Returns:
            Normalized value
        """
        if entity_type == "CURRENCY":
            # Remove currency symbols and commas
            value_text = re.sub(r'[$€£¥,]', '', text)
            try:
                return float(value_text)
            except:
                return None
        
        elif entity_type == "PERCENTAGE":
            # Remove % symbol
            value_text = text.replace('%', '').strip()
            try:
                return float(value_text) / 100.0
            except:
                return None
        
        elif entity_type == "DATE":
            # Try to parse date
            try:
                # Handle different date formats
                if '/' in text:
                    parts = text.split('/')
                    if len(parts[2]) == 2:  # MM/DD/YY
                        parts[2] = '20' + parts[2]
                    return f"{parts[2]}-{parts[0]}-{parts[1]}"  # YYYY-MM-DD
                elif '-' in text:
                    return text  # Already in YYYY-MM-DD format
                elif 'Q' in text.upper():
                    # Handle quarter format (e.g., "Q1 2023")
                    quarter = int(re.search(r'Q(\d)', text, re.IGNORECASE).group(1))
                    year = int(re.search(r'\d{4}', text).group(0))
                    month = (quarter - 1) * 3 + 1
                    return f"{year}-{month:02d}-01"  # First day of the quarter
                elif 'FY' in text.upper():
                    # Handle fiscal year format (e.g., "FY2023")
                    year = int(re.search(r'\d{4}', text).group(0))
                    return f"{year}-01-01"  # First day of the fiscal year
                else:
                    # Try to parse other formats
                    for fmt in ["%B %d, %Y", "%b %d, %Y"]:
                        try:
                            dt = datetime.strptime(text, fmt)
                            return dt.strftime("%Y-%m-%d")
                        except:
                            pass
                    return text
            except:
                return text
        
        elif entity_type == "NUMBER":
            # Remove commas and normalize suffixes
            value_text = text.replace(',', '')
            
            # Handle suffixes (K, M, B, T)
            multipliers = {
                'k': 1e3, 'm': 1e6, 'b': 1e9, 't': 1e12,
                'thousand': 1e3, 'million': 1e6, 'billion': 1e9, 'trillion': 1e12
            }
            
            for suffix, multiplier in multipliers.items():
                if suffix in value_text.lower():
                    value_text = value_text.lower().replace(suffix, '').strip()
                    try:
                        return float(value_text) * multiplier
                    except:
                        return None
            
            # No suffix, just convert to float
            try:
                return float(value_text)
            except:
                return None
        
        return text
    
    def extract_entities_from_table(self, table: pd.DataFrame) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract financial entities from a table.
        
        Args:
            table: DataFrame containing table data
            
        Returns:
            Dictionary of extracted entities by type and location
        """
        entities = {
            "currencies": [],
            "percentages": [],
            "dates": [],
            "numbers": [],
            "financial_metrics": [],
            "headers": []
        }
        
        # Process headers
        for col_idx, header in enumerate(table.columns):
            if isinstance(header, str):
                # Extract entities from header
                header_entities = self.extract_entities(header)
                
                # Add financial metrics to headers
                for metric in header_entities["financial_metrics"]:
                    entities["headers"].append({
                        "text": metric["text"],
                        "column": col_idx,
                        "category": metric["category"]
                    })
        
        # Process cells
        for row_idx, row in table.iterrows():
            for col_idx, cell in enumerate(row):
                if isinstance(cell, str):
                    # Extract entities from cell
                    cell_entities = self.extract_entities(cell)
                    
                    # Add entities with location information
                    for entity_type in ["currencies", "percentages", "dates", "numbers"]:
                        for entity in cell_entities[entity_type]:
                            entity_with_location = entity.copy()
                            entity_with_location["row"] = row_idx
                            entity_with_location["column"] = col_idx
                            entities[entity_type].append(entity_with_location)
        
        return entities
    
    def identify_financial_statement_type(self, text: str, table: Optional[pd.DataFrame] = None) -> Dict[str, float]:
        """
        Identify the type of financial statement (income statement, balance sheet, cash flow).
        
        Args:
            text: Text to analyze
            table: Optional DataFrame containing table data
            
        Returns:
            Dictionary with confidence scores for each statement type
        """
        # Keywords for each statement type
        keywords = {
            "income_statement": [
                "income statement", "profit and loss", "p&l", "statement of operations",
                "revenue", "sales", "gross profit", "operating income", "net income",
                "earnings per share", "eps", "cost of goods sold", "cogs", "expenses"
            ],
            "balance_sheet": [
                "balance sheet", "statement of financial position", "assets", "liabilities",
                "equity", "shareholders' equity", "current assets", "non-current assets",
                "current liabilities", "non-current liabilities", "total assets", "total liabilities"
            ],
            "cash_flow": [
                "cash flow", "statement of cash flows", "operating activities", "investing activities",
                "financing activities", "net cash", "cash and cash equivalents", "free cash flow"
            ]
        }
        
        # Calculate scores based on keyword matches
        scores = {statement_type: 0.0 for statement_type in keywords.keys()}
        
        # Check text for keywords
        text_lower = text.lower()
        for statement_type, statement_keywords in keywords.items():
            for keyword in statement_keywords:
                if keyword in text_lower:
                    scores[statement_type] += 1.0
        
        # Check table headers if provided
        if table is not None:
            for col in table.columns:
                if isinstance(col, str):
                    col_lower = col.lower()
                    for statement_type, statement_keywords in keywords.items():
                        for keyword in statement_keywords:
                            if keyword in col_lower:
                                scores[statement_type] += 0.5
        
        # Normalize scores
        total_score = sum(scores.values())
        if total_score > 0:
            for statement_type in scores:
                scores[statement_type] /= total_score
        
        return scores
    
    def extract_time_periods(self, text: str, table: Optional[pd.DataFrame] = None) -> List[Dict[str, Any]]:
        """
        Extract time periods from financial documents.
        
        Args:
            text: Text to analyze
            table: Optional DataFrame containing table data
            
        Returns:
            List of extracted time periods
        """
        periods = []
        
        # Extract dates from text
        entities = self.extract_entities(text)
        for date_entity in entities["dates"]:
            periods.append({
                "text": date_entity["text"],
                "value": date_entity["value"],
                "source": "text"
            })
        
        # Extract periods from table headers if provided
        if table is not None:
            for col_idx, header in enumerate(table.columns):
                if isinstance(header, str):
                    header_entities = self.extract_entities(header)
                    for date_entity in header_entities["dates"]:
                        periods.append({
                            "text": date_entity["text"],
                            "value": date_entity["value"],
                            "source": "table_header",
                            "column": col_idx
                        })
        
        # Look for period keywords
        period_patterns = [
            r'(year|quarter|month|week)(\s+ended|\s+ending)?\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},\s+\d{4}',
            r'(q[1-4]|first quarter|second quarter|third quarter|fourth quarter)(\s+of)?\s+\d{4}',
            r'(fy|fiscal year)\s*\d{4}',
            r'(ytd|year[\s-]to[\s-]date)(\s+\d{4})?',
            r'(ttm|trailing twelve months)',
            r'(mtd|month[\s-]to[\s-]date)',
            r'(qtd|quarter[\s-]to[\s-]date)'
        ]
        
        for pattern in period_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                periods.append({
                    "text": match.group(0),
                    "source": "text"
                })
        
        return periods
