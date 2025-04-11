"""
Web browsing agent implementation.
"""
import logging
from typing import Dict, List, Any, Optional
import os
import aiohttp
import json
import re
from urllib.parse import urlparse, urljoin

from .base import Agent, AgentResponse, AgentFactory
from ..services.web_service import WebService

logger = logging.getLogger(__name__)

@AgentFactory.register("web")
class WebAgent(Agent):
    """Agent that can browse the web and answer questions based on web content."""
    
    def __init__(self, agent_id: str, name: str, description: str, config: Dict[str, Any] = None):
        super().__init__(agent_id, name, description, config)
        self.api_key = config.get("api_key", os.environ.get("OPENROUTER_API_KEY", ""))
        self.model = config.get("model", "openai/gpt-4")
        self.web_service = WebService()
        self.max_pages = config.get("max_pages", 3)
        self.search_results_count = config.get("search_results_count", 5)
        
        if not self.api_key:
            logger.warning("API key not provided. Web agent will not function properly.")
    
    async def process(self, query: str, context: Dict[str, Any] = None) -> AgentResponse:
        """Process a web-related query."""
        if not self.api_key:
            return AgentResponse(
                content="Error: API key not configured. Please provide an API key.",
                metadata={"error": "api_key_missing"}
            )
        
        # Add user query to history
        self.add_to_history("user", query, context)
        
        # Determine if the query contains a URL or needs a search
        url_match = re.search(r'https?://[^\s]+', query)
        
        if url_match:
            # Extract URL from query
            url = url_match.group(0)
            return await self._process_url_query(query, url)
        else:
            # Treat as a search query
            return await self._process_search_query(query)
    
    async def _process_url_query(self, query: str, url: str) -> AgentResponse:
        """Process a query that contains a URL."""
        try:
            # Fetch the web page content
            page_content = await self.web_service.fetch_url(url)
            
            if "error" in page_content:
                return AgentResponse(
                    content=f"Error: Failed to fetch the webpage at {url}. {page_content['error_message']}",
                    metadata={"error": page_content["error"]}
                )
            
            # Create a prompt for the AI to analyze the web page
            system_prompt = f"""You are a web browsing assistant that helps users find information on the internet.
            
You are currently analyzing the content of the following webpage: {url}

Your task is to answer the user's question based on the content of this webpage.
If the answer cannot be found in the webpage content, clearly state that the information is not available on this page.
"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Here is the content of the webpage:\n\n{page_content['content']}\n\nBased on this webpage, please answer my question: {query}"}
            ]
            
            # Get AI response
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://document-understanding-demo.com",
                        "X-Title": "Document Understanding Demo"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "max_tokens": 1500,
                        "temperature": 0.3
                    }
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"API error: {error_text}")
                        return AgentResponse(
                            content=f"Error: Failed to analyze the webpage. Status code: {response.status}",
                            metadata={"error": "api_error", "status_code": response.status}
                        )
                    
                    data = await response.json()
                    
                    if not data.get("choices") or len(data["choices"]) == 0:
                        return AgentResponse(
                            content="Error: No response received from the AI model.",
                            metadata={"error": "empty_response"}
                        )
                    
                    content = data["choices"][0]["message"]["content"]
                    
                    # Add assistant response to history
                    self.add_to_history("assistant", content)
                    
                    return AgentResponse(
                        content=content,
                        metadata={
                            "url": url,
                            "title": page_content.get("title", "Unknown page"),
                            "model": data.get("model", self.model),
                            "usage": data.get("usage", {})
                        }
                    )
        
        except Exception as e:
            logger.exception(f"Error processing URL query for {url}")
            return AgentResponse(
                content=f"Error analyzing the webpage at {url}: {str(e)}",
                metadata={"error": "exception", "message": str(e)}
            )
    
    async def _process_search_query(self, query: str) -> AgentResponse:
        """Process a search query."""
        try:
            # Perform web search
            search_results = await self.web_service.search(query, max_results=self.search_results_count)
            
            if "error" in search_results:
                return AgentResponse(
                    content=f"Error: Failed to perform web search. {search_results['error_message']}",
                    metadata={"error": search_results["error"]}
                )
            
            if not search_results.get("results"):
                return AgentResponse(
                    content=f"I couldn't find any relevant search results for your query: '{query}'",
                    metadata={"error": "no_search_results"}
                )
            
            # Fetch content from top search results (limited by max_pages)
            pages_content = []
            for result in search_results["results"][:self.max_pages]:
                url = result.get("url")
                if url:
                    page_content = await self.web_service.fetch_url(url)
                    if "error" not in page_content:
                        pages_content.append({
                            "url": url,
                            "title": result.get("title", page_content.get("title", "Unknown page")),
                            "content": page_content["content"],
                            "snippet": result.get("snippet", "")
                        })
            
            if not pages_content:
                return AgentResponse(
                    content=f"I found search results for '{query}', but couldn't fetch content from any of the pages.",
                    metadata={"error": "no_page_content", "search_results": search_results["results"]}
                )
            
            # Create a prompt for the AI to analyze the search results and page contents
            search_results_text = "\n\n".join([
                f"Result {i+1}:\nTitle: {result['title']}\nURL: {result['url']}\nSnippet: {result['snippet']}"
                for i, result in enumerate(search_results["results"][:self.search_results_count])
            ])
            
            pages_content_text = "\n\n" + "\n\n".join([
                f"Page {i+1}:\nTitle: {page['title']}\nURL: {page['url']}\nContent:\n{page['content'][:5000]}..."  # Truncate content to avoid token limits
                for i, page in enumerate(pages_content)
            ])
            
            system_prompt = f"""You are a web browsing assistant that helps users find information on the internet.
            
You have performed a web search for the query: "{query}"

Your task is to:
1. Analyze the search results and web page contents
2. Provide a comprehensive answer to the user's query based on the information found
3. Cite your sources by mentioning the relevant URLs
4. If the information is not found in the search results, clearly state that

Be concise but thorough in your response.
"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Here are the search results:\n\n{search_results_text}\n\nHere is the content of the top {len(pages_content)} pages:{pages_content_text}\n\nBased on these search results and page contents, please answer my question: {query}"}
            ]
            
            # Get AI response
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://document-understanding-demo.com",
                        "X-Title": "Document Understanding Demo"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "max_tokens": 1500,
                        "temperature": 0.3
                    }
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"API error: {error_text}")
                        return AgentResponse(
                            content=f"Error: Failed to analyze the search results. Status code: {response.status}",
                            metadata={"error": "api_error", "status_code": response.status}
                        )
                    
                    data = await response.json()
                    
                    if not data.get("choices") or len(data["choices"]) == 0:
                        return AgentResponse(
                            content="Error: No response received from the AI model.",
                            metadata={"error": "empty_response"}
                        )
                    
                    content = data["choices"][0]["message"]["content"]
                    
                    # Add assistant response to history
                    self.add_to_history("assistant", content)
                    
                    return AgentResponse(
                        content=content,
                        metadata={
                            "search_query": query,
                            "search_results": [{"url": r["url"], "title": r["title"]} for r in search_results["results"][:self.search_results_count]],
                            "pages_analyzed": [{"url": p["url"], "title": p["title"]} for p in pages_content],
                            "model": data.get("model", self.model),
                            "usage": data.get("usage", {})
                        }
                    )
        
        except Exception as e:
            logger.exception(f"Error processing search query: {query}")
            return AgentResponse(
                content=f"Error searching the web for '{query}': {str(e)}",
                metadata={"error": "exception", "message": str(e)}
            )
