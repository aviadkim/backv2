"""
Financial agents for document analysis.
"""
import os
import logging
from typing import Dict, List, Any, Optional, Union
import json
import datetime

from financial_document_processor.database.db import Database
from financial_document_processor.agents.config import AIConfig
from financial_document_processor.agents.document_index import DocumentIndex

# Try to import LangChain
try:
    from langchain.agents import AgentExecutor, create_openai_functions_agent
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain.tools import BaseTool, StructuredTool, tool
    from langchain.schema import SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logging.warning("LangChain library not available. Install with: pip install langchain")

class FinancialAgentBase:
    """Base class for financial agents."""
    
    def __init__(self, database: Database, ai_config: AIConfig, document_index: DocumentIndex):
        """
        Initialize the financial agent.
        
        Args:
            database: Database connection
            ai_config: AI configuration
            document_index: Document index
        """
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain library not available. Install with: pip install langchain")
        
        self.database = database
        self.ai_config = ai_config
        self.document_index = document_index
        self.llm = ai_config.get_llm_config()["llm"]
    
    def _create_agent(self, system_message: str, tools: List[BaseTool]) -> AgentExecutor:
        """
        Create a LangChain agent.
        
        Args:
            system_message: System message for the agent
            tools: List of tools for the agent
        
        Returns:
            AgentExecutor
        """
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        agent = create_openai_functions_agent(self.llm, tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            return_intermediate_steps=True
        )
        
        return agent_executor


class FinancialQueryAgent(FinancialAgentBase):
    """Agent for querying financial documents."""
    
    def __init__(self, database: Database, ai_config: AIConfig, document_index: DocumentIndex):
        """Initialize the financial query agent."""
        super().__init__(database, ai_config, document_index)
        
        # Create tools
        self.tools = self._create_tools()
        
        # Create agent
        system_message = """
        You are a financial document analysis assistant. Your job is to help users understand their financial documents
        and extract insights from them. You can answer questions about portfolio values, securities, asset allocations,
        and other financial information contained in the documents.
        
        Always be precise and accurate with financial data. If you're not sure about something, say so rather than guessing.
        When reporting monetary values, always include the currency and format numbers appropriately with commas as thousand separators.
        
        Use the available tools to query the document index and retrieve information from the database.
        """
        
        self.agent = self._create_agent(system_message, self.tools)
    
    def _create_tools(self) -> List[BaseTool]:
        """
        Create tools for the agent.
        
        Returns:
            List of tools
        """
        tools = []
        
        @tool
        def query_document(query: str, document_id: Optional[int] = None) -> str:
            """
            Query the document index for information.
            
            Args:
                query: The question or query about the financial document
                document_id: Optional document ID to limit the search to a specific document
            
            Returns:
                Answer to the query based on the document content
            """
            result = self.document_index.query(query, document_id)
            return result["response"]
        
        @tool
        def get_document_list() -> str:
            """
            Get a list of available documents.
            
            Returns:
                List of documents with their IDs and metadata
            """
            with self.database.get_session() as session:
                from financial_document_processor.database.models import Document
                documents = session.query(Document).all()
                
                result = "Available documents:\n\n"
                for doc in documents:
                    result += f"ID: {doc.id}\n"
                    result += f"Filename: {doc.filename}\n"
                    result += f"Type: {doc.document_type or 'N/A'}\n"
                    result += f"Status: {doc.processing_status}\n"
                    result += f"Extraction Date: {doc.extraction_date.strftime('%Y-%m-%d') if doc.extraction_date else 'N/A'}\n\n"
                
                return result
        
        @tool
        def get_portfolio_value(document_id: int) -> str:
            """
            Get the portfolio value for a document.
            
            Args:
                document_id: Document ID
            
            Returns:
                Portfolio value information
            """
            portfolio_value = self.database.get_portfolio_value(document_id)
            
            if not portfolio_value:
                return f"No portfolio value found for document ID {document_id}"
            
            result = f"Portfolio Value: {portfolio_value.value:,.2f} {portfolio_value.currency or 'USD'}\n"
            result += f"Date: {portfolio_value.value_date.strftime('%Y-%m-%d') if portfolio_value.value_date else 'N/A'}\n"
            
            return result
        
        @tool
        def get_securities(document_id: int) -> str:
            """
            Get securities for a document.
            
            Args:
                document_id: Document ID
            
            Returns:
                Securities information
            """
            securities = self.database.get_securities(document_id)
            
            if not securities:
                return f"No securities found for document ID {document_id}"
            
            result = f"Found {len(securities)} securities in document ID {document_id}:\n\n"
            
            for i, security in enumerate(securities[:20]):  # Limit to 20 securities to avoid too long responses
                result += f"{i+1}. "
                result += f"ISIN: {security.isin or 'N/A'}\n"
                result += f"   Name: {security.name or security.description or 'N/A'}\n"
                result += f"   Type: {security.security_type or 'N/A'}\n"
                result += f"   Asset Class: {security.asset_class or 'N/A'}\n"
                result += f"   Valuation: {security.valuation:,.2f} {security.currency or 'USD'}\n" if security.valuation else f"   Valuation: N/A\n"
                result += f"   Price: {security.price:,.2f}\n" if security.price else f"   Price: N/A\n"
                result += f"   Quantity: {security.quantity:,.2f}\n" if security.quantity else f"   Quantity: N/A\n"
                result += "\n"
            
            if len(securities) > 20:
                result += f"... and {len(securities) - 20} more securities"
            
            return result
        
        @tool
        def get_asset_allocations(document_id: int) -> str:
            """
            Get asset allocations for a document.
            
            Args:
                document_id: Document ID
            
            Returns:
                Asset allocations information
            """
            asset_allocations = self.database.get_asset_allocations(document_id)
            
            if not asset_allocations:
                return f"No asset allocations found for document ID {document_id}"
            
            result = f"Found {len(asset_allocations)} asset allocations in document ID {document_id}:\n\n"
            
            for i, allocation in enumerate(asset_allocations):
                result += f"{i+1}. Asset Class: {allocation.asset_class}\n"
                result += f"   Value: {allocation.value:,.2f} {allocation.currency or 'USD'}\n" if allocation.value else f"   Value: N/A\n"
                result += f"   Percentage: {allocation.percentage:.2f}%\n" if allocation.percentage else f"   Percentage: N/A\n"
                result += "\n"
            
            return result
        
        @tool
        def get_top_holdings(document_id: int, limit: int = 5) -> str:
            """
            Get top holdings for a document.
            
            Args:
                document_id: Document ID
                limit: Number of top holdings to return (default: 5)
            
            Returns:
                Top holdings information
            """
            securities = self.database.get_securities(document_id)
            
            if not securities:
                return f"No securities found for document ID {document_id}"
            
            # Filter securities with valuation
            securities_with_valuation = [s for s in securities if s.valuation is not None]
            
            if not securities_with_valuation:
                return f"No securities with valuation found for document ID {document_id}"
            
            # Sort by valuation (descending)
            securities_with_valuation.sort(key=lambda s: s.valuation or 0, reverse=True)
            
            # Get top holdings
            top_holdings = securities_with_valuation[:limit]
            
            result = f"Top {len(top_holdings)} holdings in document ID {document_id}:\n\n"
            
            for i, security in enumerate(top_holdings):
                result += f"{i+1}. "
                result += f"ISIN: {security.isin or 'N/A'}\n"
                result += f"   Name: {security.name or security.description or 'N/A'}\n"
                result += f"   Type: {security.security_type or 'N/A'}\n"
                result += f"   Asset Class: {security.asset_class or 'N/A'}\n"
                result += f"   Valuation: {security.valuation:,.2f} {security.currency or 'USD'}\n"
                result += "\n"
            
            return result
        
        tools.extend([
            query_document,
            get_document_list,
            get_portfolio_value,
            get_securities,
            get_asset_allocations,
            get_top_holdings
        ])
        
        return tools
    
    def query(self, query_text: str, document_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Query the agent.
        
        Args:
            query_text: Query text
            document_id: Document ID (optional)
        
        Returns:
            Dictionary with query results
        """
        # Prepare input
        input_text = query_text
        if document_id is not None:
            input_text = f"For document ID {document_id}: {query_text}"
        
        # Execute agent
        result = self.agent.invoke({"input": input_text, "chat_history": []})
        
        return {
            "query": query_text,
            "document_id": document_id,
            "response": result["output"],
            "intermediate_steps": result.get("intermediate_steps", [])
        }


class TableGenerationAgent(FinancialAgentBase):
    """Agent for generating tables from financial documents."""
    
    def __init__(self, database: Database, ai_config: AIConfig, document_index: DocumentIndex):
        """Initialize the table generation agent."""
        super().__init__(database, ai_config, document_index)
        
        # Create tools
        self.tools = self._create_tools()
        
        # Create agent
        system_message = """
        You are a financial table generation assistant. Your job is to create well-structured tables based on financial
        data in documents. You can generate tables for portfolio summaries, asset allocations, securities lists,
        performance metrics, and other financial information.
        
        Always ensure that tables are well-formatted and include appropriate headers. Format numbers consistently
        with commas as thousand separators and appropriate decimal places. Include currency symbols where applicable.
        
        Use the available tools to query the document index and retrieve information from the database.
        """
        
        self.agent = self._create_agent(system_message, self.tools)
    
    def _create_tools(self) -> List[BaseTool]:
        """
        Create tools for the agent.
        
        Returns:
            List of tools
        """
        tools = []
        
        @tool
        def query_document(query: str, document_id: Optional[int] = None) -> str:
            """
            Query the document index for information.
            
            Args:
                query: The question or query about the financial document
                document_id: Optional document ID to limit the search to a specific document
            
            Returns:
                Answer to the query based on the document content
            """
            result = self.document_index.query(query, document_id)
            return result["response"]
        
        @tool
        def get_securities_data(document_id: int) -> str:
            """
            Get securities data for a document in a format suitable for table generation.
            
            Args:
                document_id: Document ID
            
            Returns:
                Securities data in JSON format
            """
            securities = self.database.get_securities(document_id)
            
            if not securities:
                return json.dumps({"error": f"No securities found for document ID {document_id}"})
            
            securities_data = []
            for security in securities:
                data = {
                    "isin": security.isin,
                    "name": security.name or security.description,
                    "type": security.security_type,
                    "asset_class": security.asset_class,
                    "valuation": security.valuation,
                    "currency": security.currency or "USD",
                    "price": security.price,
                    "quantity": security.quantity
                }
                securities_data.append(data)
            
            return json.dumps({"securities": securities_data})
        
        @tool
        def get_asset_allocation_data(document_id: int) -> str:
            """
            Get asset allocation data for a document in a format suitable for table generation.
            
            Args:
                document_id: Document ID
            
            Returns:
                Asset allocation data in JSON format
            """
            asset_allocations = self.database.get_asset_allocations(document_id)
            
            if not asset_allocations:
                return json.dumps({"error": f"No asset allocations found for document ID {document_id}"})
            
            allocation_data = []
            for allocation in asset_allocations:
                data = {
                    "asset_class": allocation.asset_class,
                    "value": allocation.value,
                    "percentage": allocation.percentage,
                    "currency": allocation.currency or "USD"
                }
                allocation_data.append(data)
            
            return json.dumps({"asset_allocations": allocation_data})
        
        @tool
        def generate_html_table(data: List[Dict[str, Any]], headers: List[str], 
                               title: Optional[str] = None) -> str:
            """
            Generate an HTML table from data.
            
            Args:
                data: List of dictionaries with data
                headers: List of headers (should match keys in data dictionaries)
                title: Optional table title
            
            Returns:
                HTML table
            """
            html = "<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse;'>\n"
            
            # Add title if provided
            if title:
                html += f"<caption style='font-weight: bold; font-size: 1.2em; margin-bottom: 10px;'>{title}</caption>\n"
            
            # Add headers
            html += "<thead>\n<tr>\n"
            for header in headers:
                html += f"<th style='background-color: #f2f2f2;'>{header}</th>\n"
            html += "</tr>\n</thead>\n"
            
            # Add data
            html += "<tbody>\n"
            for row in data:
                html += "<tr>\n"
                for header in headers:
                    value = row.get(header, "")
                    
                    # Format numbers
                    if isinstance(value, (int, float)):
                        if header.lower() in ["percentage", "percent"]:
                            value = f"{value:.2f}%"
                        elif value >= 1000:
                            value = f"{value:,.2f}"
                        else:
                            value = f"{value:.2f}"
                    
                    html += f"<td>{value}</td>\n"
                html += "</tr>\n"
            html += "</tbody>\n"
            
            html += "</table>"
            return html
        
        @tool
        def generate_markdown_table(data: List[Dict[str, Any]], headers: List[str], 
                                  title: Optional[str] = None) -> str:
            """
            Generate a Markdown table from data.
            
            Args:
                data: List of dictionaries with data
                headers: List of headers (should match keys in data dictionaries)
                title: Optional table title
            
            Returns:
                Markdown table
            """
            markdown = ""
            
            # Add title if provided
            if title:
                markdown += f"## {title}\n\n"
            
            # Add headers
            markdown += "| " + " | ".join(headers) + " |\n"
            markdown += "| " + " | ".join(["---"] * len(headers)) + " |\n"
            
            # Add data
            for row in data:
                row_values = []
                for header in headers:
                    value = row.get(header, "")
                    
                    # Format numbers
                    if isinstance(value, (int, float)):
                        if header.lower() in ["percentage", "percent"]:
                            value = f"{value:.2f}%"
                        elif value >= 1000:
                            value = f"{value:,.2f}"
                        else:
                            value = f"{value:.2f}"
                    
                    row_values.append(str(value))
                
                markdown += "| " + " | ".join(row_values) + " |\n"
            
            return markdown
        
        @tool
        def generate_csv_data(data: List[Dict[str, Any]], headers: List[str]) -> str:
            """
            Generate CSV data.
            
            Args:
                data: List of dictionaries with data
                headers: List of headers (should match keys in data dictionaries)
            
            Returns:
                CSV data
            """
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            writer.writerow(headers)
            
            # Write data
            for row in data:
                row_values = []
                for header in headers:
                    value = row.get(header, "")
                    row_values.append(value)
                
                writer.writerow(row_values)
            
            return output.getvalue()
        
        tools.extend([
            query_document,
            get_securities_data,
            get_asset_allocation_data,
            generate_html_table,
            generate_markdown_table,
            generate_csv_data
        ])
        
        return tools
    
    def generate_table(self, request: str, document_id: int, format: str = "markdown") -> Dict[str, Any]:
        """
        Generate a table.
        
        Args:
            request: Table generation request
            document_id: Document ID
            format: Output format (markdown, html, or csv)
        
        Returns:
            Dictionary with table generation results
        """
        # Prepare input
        input_text = f"For document ID {document_id}, generate a {format} table for: {request}"
        
        # Execute agent
        result = self.agent.invoke({"input": input_text, "chat_history": []})
        
        return {
            "request": request,
            "document_id": document_id,
            "format": format,
            "table": result["output"],
            "intermediate_steps": result.get("intermediate_steps", [])
        }


class FinancialAnalysisAgent(FinancialAgentBase):
    """Agent for financial analysis."""
    
    def __init__(self, database: Database, ai_config: AIConfig, document_index: DocumentIndex):
        """Initialize the financial analysis agent."""
        super().__init__(database, ai_config, document_index)
        
        # Create tools
        self.tools = self._create_tools()
        
        # Create agent
        system_message = """
        You are a financial analysis assistant. Your job is to analyze financial documents and provide insights
        and recommendations based on the data. You can analyze portfolio composition, asset allocation, performance,
        risk, and other financial metrics.
        
        Always provide well-reasoned analysis based on the data. Explain your reasoning and provide context for your
        insights. When making recommendations, consider the user's goals and risk tolerance if available.
        
        Use the available tools to query the document index and retrieve information from the database.
        """
        
        self.agent = self._create_agent(system_message, self.tools)
    
    def _create_tools(self) -> List[BaseTool]:
        """
        Create tools for the agent.
        
        Returns:
            List of tools
        """
        tools = []
        
        @tool
        def query_document(query: str, document_id: Optional[int] = None) -> str:
            """
            Query the document index for information.
            
            Args:
                query: The question or query about the financial document
                document_id: Optional document ID to limit the search to a specific document
            
            Returns:
                Answer to the query based on the document content
            """
            result = self.document_index.query(query, document_id)
            return result["response"]
        
        @tool
        def get_portfolio_summary(document_id: int) -> str:
            """
            Get a portfolio summary for a document.
            
            Args:
                document_id: Document ID
            
            Returns:
                Portfolio summary information
            """
            # Get portfolio value
            portfolio_value = self.database.get_portfolio_value(document_id)
            
            # Get securities
            securities = self.database.get_securities(document_id)
            
            # Get asset allocations
            asset_allocations = self.database.get_asset_allocations(document_id)
            
            # Create summary
            summary = "Portfolio Summary:\n\n"
            
            if portfolio_value:
                summary += f"Portfolio Value: {portfolio_value.value:,.2f} {portfolio_value.currency or 'USD'}\n"
                summary += f"Date: {portfolio_value.value_date.strftime('%Y-%m-%d') if portfolio_value.value_date else 'N/A'}\n\n"
            
            if securities:
                summary += f"Securities Count: {len(securities)}\n"
                
                # Calculate total valuation
                total_valuation = sum(s.valuation or 0 for s in securities)
                summary += f"Total Securities Valuation: {total_valuation:,.2f} USD\n\n"
                
                # Count by security type
                security_types = {}
                for security in securities:
                    security_type = security.security_type or "Unknown"
                    security_types[security_type] = security_types.get(security_type, 0) + 1
                
                summary += "Security Types:\n"
                for security_type, count in security_types.items():
                    summary += f"- {security_type}: {count}\n"
                summary += "\n"
            
            if asset_allocations:
                summary += "Asset Allocation:\n"
                for allocation in asset_allocations:
                    summary += f"- {allocation.asset_class}: "
                    if allocation.percentage:
                        summary += f"{allocation.percentage:.2f}%"
                    if allocation.value:
                        summary += f" ({allocation.value:,.2f} {allocation.currency or 'USD'})"
                    summary += "\n"
            
            return summary
        
        @tool
        def analyze_asset_allocation(document_id: int) -> str:
            """
            Analyze asset allocation for a document.
            
            Args:
                document_id: Document ID
            
            Returns:
                Asset allocation analysis
            """
            # Get asset allocations
            asset_allocations = self.database.get_asset_allocations(document_id)
            
            if not asset_allocations:
                return f"No asset allocations found for document ID {document_id}"
            
            # Create analysis
            analysis = "Asset Allocation Analysis:\n\n"
            
            # Sort by percentage (descending)
            asset_allocations.sort(key=lambda a: a.percentage or 0, reverse=True)
            
            # Calculate total percentage and value
            total_percentage = sum(a.percentage or 0 for a in asset_allocations)
            total_value = sum(a.value or 0 for a in asset_allocations)
            
            analysis += f"Total Allocation: {total_percentage:.2f}% ({total_value:,.2f} USD)\n\n"
            
            # List allocations
            analysis += "Allocations by Asset Class:\n"
            for allocation in asset_allocations:
                analysis += f"- {allocation.asset_class}: "
                if allocation.percentage:
                    analysis += f"{allocation.percentage:.2f}%"
                if allocation.value:
                    analysis += f" ({allocation.value:,.2f} {allocation.currency or 'USD'})"
                analysis += "\n"
            
            return analysis
        
        @tool
        def analyze_top_holdings(document_id: int, limit: int = 10) -> str:
            """
            Analyze top holdings for a document.
            
            Args:
                document_id: Document ID
                limit: Number of top holdings to analyze (default: 10)
            
            Returns:
                Top holdings analysis
            """
            # Get securities
            securities = self.database.get_securities(document_id)
            
            if not securities:
                return f"No securities found for document ID {document_id}"
            
            # Filter securities with valuation
            securities_with_valuation = [s for s in securities if s.valuation is not None]
            
            if not securities_with_valuation:
                return f"No securities with valuation found for document ID {document_id}"
            
            # Sort by valuation (descending)
            securities_with_valuation.sort(key=lambda s: s.valuation or 0, reverse=True)
            
            # Get top holdings
            top_holdings = securities_with_valuation[:limit]
            
            # Get portfolio value
            portfolio_value = self.database.get_portfolio_value(document_id)
            total_portfolio_value = portfolio_value.value if portfolio_value else sum(s.valuation or 0 for s in securities_with_valuation)
            
            # Create analysis
            analysis = f"Top {len(top_holdings)} Holdings Analysis:\n\n"
            
            if total_portfolio_value:
                analysis += f"Total Portfolio Value: {total_portfolio_value:,.2f} USD\n\n"
            
            # Calculate concentration metrics
            top_holdings_value = sum(s.valuation or 0 for s in top_holdings)
            top_holdings_percentage = (top_holdings_value / total_portfolio_value) * 100 if total_portfolio_value else 0
            
            analysis += f"Top {len(top_holdings)} Holdings Value: {top_holdings_value:,.2f} USD ({top_holdings_percentage:.2f}% of portfolio)\n\n"
            
            # List top holdings
            analysis += "Top Holdings:\n"
            for i, security in enumerate(top_holdings):
                percentage = ((security.valuation or 0) / total_portfolio_value) * 100 if total_portfolio_value else 0
                analysis += f"{i+1}. {security.name or security.description or security.isin or 'Unknown'}: "
                analysis += f"{security.valuation:,.2f} {security.currency or 'USD'} ({percentage:.2f}% of portfolio)\n"
            
            return analysis
        
        @tool
        def generate_investment_recommendations(document_id: int) -> str:
            """
            Generate investment recommendations based on portfolio analysis.
            
            Args:
                document_id: Document ID
            
            Returns:
                Investment recommendations
            """
            # This is a placeholder for a more sophisticated recommendation engine
            # In a real implementation, this would analyze the portfolio and generate personalized recommendations
            
            # Get portfolio summary
            portfolio_summary = self.get_portfolio_summary(document_id)
            
            # Generate recommendations using AI
            prompt = f"""
            Based on the following portfolio summary, generate investment recommendations:
            
            {portfolio_summary}
            
            Please provide 3-5 specific recommendations for portfolio optimization, considering:
            1. Asset allocation
            2. Diversification
            3. Risk management
            4. Tax efficiency
            5. Cost reduction
            
            For each recommendation, provide a brief rationale.
            """
            
            recommendations = self.ai_config.generate_completion(prompt)
            
            return f"Investment Recommendations:\n\n{recommendations}"
        
        tools.extend([
            query_document,
            get_portfolio_summary,
            analyze_asset_allocation,
            analyze_top_holdings,
            generate_investment_recommendations
        ])
        
        return tools
    
    def analyze(self, request: str, document_id: int) -> Dict[str, Any]:
        """
        Perform financial analysis.
        
        Args:
            request: Analysis request
            document_id: Document ID
        
        Returns:
            Dictionary with analysis results
        """
        # Prepare input
        input_text = f"For document ID {document_id}, analyze: {request}"
        
        # Execute agent
        result = self.agent.invoke({"input": input_text, "chat_history": []})
        
        return {
            "request": request,
            "document_id": document_id,
            "analysis": result["output"],
            "intermediate_steps": result.get("intermediate_steps", [])
        }
