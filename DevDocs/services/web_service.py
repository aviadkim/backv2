"""
Web service for fetching web pages and performing searches.
"""
import logging
import aiohttp
import os
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
import json
import re

logger = logging.getLogger(__name__)

class WebService:
    """Service for web browsing and searching."""
    
    def __init__(self):
        self.search_api_key = os.environ.get("SERP_API_KEY", "")
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    async def fetch_url(self, url: str) -> Dict[str, Any]:
        """Fetch content from a URL."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers={"User-Agent": self.user_agent},
                    timeout=30
                ) as response:
                    if response.status != 200:
                        return {
                            "error": "http_error",
                            "error_message": f"HTTP error {response.status}",
                            "status_code": response.status
                        }
                    
                    html = await response.text()
                    
                    # Parse HTML with BeautifulSoup
                    soup = BeautifulSoup(html, "html.parser")
                    
                    # Extract title
                    title = soup.title.string if soup.title else "No title"
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.extract()
                    
                    # Get text content
                    text = soup.get_text(separator="\n")
                    
                    # Clean up text (remove excessive whitespace)
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = "\n".join(chunk for chunk in chunks if chunk)
                    
                    return {
                        "url": url,
                        "title": title,
                        "content": text,
                        "html": html  # Include raw HTML in case it's needed
                    }
        
        except aiohttp.ClientError as e:
            logger.exception(f"Client error fetching URL {url}")
            return {
                "error": "client_error",
                "error_message": f"Failed to connect to {url}: {str(e)}"
            }
        except Exception as e:
            logger.exception(f"Error fetching URL {url}")
            return {
                "error": "fetch_error",
                "error_message": f"Error fetching {url}: {str(e)}"
            }
    
    async def search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Perform a web search."""
        if not self.search_api_key:
            # Fallback to a mock search if no API key is provided
            return self._mock_search(query, max_results)
        
        try:
            # Use SerpAPI for real search results
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://serpapi.com/search",
                    params={
                        "q": query,
                        "api_key": self.search_api_key,
                        "engine": "google",
                        "num": max_results
                    }
                ) as response:
                    if response.status != 200:
                        return {
                            "error": "search_api_error",
                            "error_message": f"Search API returned status code {response.status}",
                            "status_code": response.status
                        }
                    
                    data = await response.json()
                    
                    if "error" in data:
                        return {
                            "error": "search_api_error",
                            "error_message": data["error"]
                        }
                    
                    organic_results = data.get("organic_results", [])
                    
                    results = []
                    for result in organic_results[:max_results]:
                        results.append({
                            "title": result.get("title", "No title"),
                            "url": result.get("link", ""),
                            "snippet": result.get("snippet", "")
                        })
                    
                    return {
                        "query": query,
                        "results": results
                    }
        
        except Exception as e:
            logger.exception(f"Error performing search for query: {query}")
            return {
                "error": "search_error",
                "error_message": f"Error performing search: {str(e)}"
            }
    
    def _mock_search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Provide mock search results when no API key is available."""
        logger.warning("Using mock search results as no SERP API key is provided")
        
        # Generate some mock results based on the query
        results = []
        
        # Add a disclaimer result
        results.append({
            "title": "Mock Search Result - API Key Required",
            "url": "https://example.com/mock-search",
            "snippet": "This is a mock search result. To get real search results, please provide a SERP API key."
        })
        
        # Add some generic results based on the query
        query_words = re.sub(r'[^\w\s]', '', query.lower()).split()
        
        mock_domains = ["example.com", "mockdata.org", "sampleresults.net", "testinfo.com", "demopage.io"]
        
        for i in range(1, min(max_results, 5)):
            domain = mock_domains[i % len(mock_domains)]
            query_slug = "-".join(query_words[:3]) if query_words else "search"
            
            results.append({
                "title": f"Mock Result {i} for {query}",
                "url": f"https://{domain}/{query_slug}-result-{i}",
                "snippet": f"This is mock search result #{i} for the query '{query}'. This would contain a snippet of text from the page that matches your search terms."
            })
        
        return {
            "query": query,
            "results": results,
            "is_mock": True
        }
