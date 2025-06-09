"""Simple web search implementation for fallback when Google Search API is not available."""

import asyncio
from typing import List, Dict, Any
import time


async def simple_web_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Perform a simple web search using DuckDuckGo (free, no API key required).
    Uses asyncio.to_thread to avoid blocking the event loop.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        List of search results with title, url, and snippet
    """
    try:
        # Import DuckDuckGo search inside the function to handle import errors gracefully
        from duckduckgo_search import DDGS
        
        # Use asyncio.to_thread to run the blocking DuckDuckGo search in a separate thread
        search_results = await asyncio.to_thread(
            lambda: list(DDGS().text(query, max_results=max_results))
        )
        
        results = []
        for i, result in enumerate(search_results):
            title = result.get('title', '')
            url = result.get('href', '')
            snippet = result.get('body', '')
            
            if title and url and snippet:
                results.append({
                    'title': title,
                    'url': url,
                    'snippet': snippet,
                    'label': title[:50] + '...' if len(title) > 50 else title,
                    'value': url,
                    'short_url': f"[{i+1}]"
                })
        
        return results
        
    except ImportError:
        print("Error: duckduckgo_search is not installed. Install it with: pip install duckduckgo-search")
        return []
    except Exception as e:
        print(f"Error performing web search: {e}")
        return []


def format_search_results_for_llm(results: List[Dict[str, Any]], query: str) -> str:
    """
    Format search results for LLM consumption.
    
    Args:
        results: List of search results
        query: Original search query
        
    Returns:
        Formatted string with search results
    """
    if not results:
        return f"No search results found for query: {query}"
    
    formatted_results = f"Search results for '{query}':\n\n"
    
    for i, result in enumerate(results, 1):
        formatted_results += f"{i}. **{result['title']}**\n"
        formatted_results += f"   URL: {result['url']}\n"
        formatted_results += f"   Summary: {result['snippet']}\n"
        formatted_results += f"   Citation: {result['short_url']}\n\n"
    
    return formatted_results


async def perform_web_search_with_llm(
    search_query: str,
    llm: Any,
    search_prompt_template: str,
    max_results: int = 5
) -> Dict[str, Any]:
    """
    Perform web search and process results with LLM.
    
    Args:
        search_query: The search query
        llm: The LLM instance to process results
        search_prompt_template: Template for the search prompt
        max_results: Maximum number of search results
        
    Returns:
        Dictionary with processed search results
    """
    # Perform the web search
    search_results = await simple_web_search(search_query, max_results)
    
    if not search_results:
        return {
            "sources_gathered": [],
            "search_query": search_query,
            "web_research_result": f"No search results found for: {search_query}"
        }
    
    # Format results for LLM processing
    formatted_results = format_search_results_for_llm(search_results, search_query)
    
    # Create sources in the expected format - define this outside the try block
    sources_gathered = []
    for result in search_results:
        sources_gathered.append({
            'label': result['label'],
            'value': result['value'],
            'short_url': result['short_url']
        })
    
    # Create prompt for LLM to process the search results
    prompt = search_prompt_template.format(
        current_date=time.strftime("%Y-%m-%d"),
        research_topic=search_query,
        search_results=formatted_results
    )
    
    try:
        # Process with LLM
        response = llm.invoke(prompt)
        processed_content = response.content if hasattr(response, 'content') else str(response)
        
        return {
            "sources_gathered": sources_gathered,
            "search_query": search_query,
            "web_research_result": processed_content
        }
        
    except Exception as e:
        print(f"Error processing search results with LLM: {e}")
        return {
            "sources_gathered": sources_gathered,
            "search_query": search_query,
            "web_research_result": formatted_results
        } 