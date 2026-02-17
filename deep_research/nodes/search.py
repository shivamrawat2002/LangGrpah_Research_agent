"""
Search execution node for the research graph.
"""

import os
import asyncio
from ..state import ResearchState, Source
from ..tools import get_firecrawl_client


async def search_node(state: ResearchState) -> dict:
    """
    Execute searches for all generated queries.
    
    This node:
    1. Takes the generated search queries
    2. Executes searches concurrently using Firecrawl
    3. Collects and structures results
    
    Args:
        state: Current research state
        
    Returns:
        Updated state with search_results and all_sources
    """
    queries = state.get("search_queries", [])
    if not queries:
        print("⚠️ No queries to search")
        return {"search_results": [], "all_sources": []}
    
    print(f"\n🌐 Executing {len(queries)} searches...")
    
    # Get concurrency limit from environment
    concurrency_limit = int(os.getenv("CONCURRENCY_LIMIT", "3"))
    
    # Get Firecrawl client and perform searches
    client = get_firecrawl_client()
    search_results_dict = await client.batch_search(
        queries=queries,
        num_results=5,
        concurrency_limit=concurrency_limit,
    )
    
    # Structure results and sources
    all_results = []
    new_sources = []
    
    for query, results in search_results_dict.items():
        print(f"  📄 {query}: {len(results)} results")
        
        for result in results:
            all_results.append({
                "query": query,
                "url": result["url"],
                "title": result["title"],
                "content": result["content"],
            })
            
            # Add to sources
            new_sources.append(Source(
                url=result["url"],
                title=result["title"],
                content=result["content"],
            ))
    
    print(f"✅ Retrieved {len(all_results)} total results from {len(queries)} queries")
    
    return {
        "search_results": all_results,
        "all_sources": new_sources,
    }
