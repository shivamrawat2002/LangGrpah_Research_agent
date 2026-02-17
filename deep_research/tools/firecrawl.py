"""
Firecrawl integration for web search and content extraction.
"""

import os
import asyncio
from typing import Any
import httpx


class FirecrawlClient:
    """
    Client for Firecrawl API supporting search and content extraction.
    """
    
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY", "")
        self.base_url = base_url or os.getenv(
            "FIRECRAWL_BASE_URL",
            "https://api.firecrawl.dev"
        )
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    async def search(
        self,
        query: str,
        num_results: int = 5,
        timeout: int = 30,
    ) -> list[dict[str, Any]]:
        """
        Perform a web search using Firecrawl.
        
        Args:
            query: The search query
            num_results: Number of results to return
            timeout: Request timeout in seconds
            
        Returns:
            List of search results with url, title, and content
        """
        url = f"{self.base_url}/v1/search"
        payload = {
            "query": query,
            "limit": num_results,
            "scrapeOptions": {
                "formats": ["markdown"],
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract results
                results = []
                for item in data.get("data", []):
                    results.append({
                        "url": item.get("url", ""),
                        "title": item.get("title", ""),
                        "content": item.get("markdown", ""),
                    })
                
                return results
                
        except httpx.HTTPError as e:
            print(f"Error searching with Firecrawl: {e}")
            return []
    
    async def scrape(
        self,
        url: str,
        timeout: int = 30,
    ) -> dict[str, Any]:
        """
        Scrape content from a URL using Firecrawl.
        
        Args:
            url: The URL to scrape
            timeout: Request timeout in seconds
            
        Returns:
            Scraped content with url, title, and markdown
        """
        endpoint = f"{self.base_url}/v1/scrape"
        payload = {
            "url": url,
            "formats": ["markdown"],
        }
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    endpoint,
                    json=payload,
                    headers=self.headers,
                )
                response.raise_for_status()
                data = response.json()
                
                return {
                    "url": url,
                    "title": data.get("data", {}).get("title", ""),
                    "content": data.get("data", {}).get("markdown", ""),
                }
                
        except httpx.HTTPError as e:
            print(f"Error scraping URL {url}: {e}")
            return {"url": url, "title": "", "content": ""}
    
    async def batch_search(
        self,
        queries: list[str],
        num_results: int = 5,
        concurrency_limit: int = 3,
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Perform multiple searches concurrently.
        
        Args:
            queries: List of search queries
            num_results: Number of results per query
            concurrency_limit: Maximum concurrent requests
            
        Returns:
            Dictionary mapping queries to their results
        """
        semaphore = asyncio.Semaphore(concurrency_limit)
        
        async def search_with_limit(query: str):
            async with semaphore:
                results = await self.search(query, num_results)
                return query, results
        
        tasks = [search_with_limit(q) for q in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and build result dict
        search_results = {}
        for result in results:
            if isinstance(result, Exception):
                print(f"Search failed: {result}")
                continue
            query, query_results = result
            search_results[query] = query_results
        
        return search_results


# Singleton instance
_firecrawl_client: FirecrawlClient | None = None


def get_firecrawl_client() -> FirecrawlClient:
    """Get or create the Firecrawl client singleton."""
    global _firecrawl_client
    if _firecrawl_client is None:
        _firecrawl_client = FirecrawlClient()
    return _firecrawl_client
