"""Simple web search implementation for fallback when Google Search API is not available."""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import time
import urllib.parse


def simple_web_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Perform a simple web search using DuckDuckGo (free, no API key required).
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        List of search results with title, url, and snippet
    """
    try:
        # Use DuckDuckGo's HTML search (no API key required)
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        results = []
        
        # Parse DuckDuckGo results
        for result_div in soup.find_all('div', class_='result')[:max_results]:
            try:
                title_elem = result_div.find('a', class_='result__a')
                snippet_elem = result_div.find('a', class_='result__snippet')
                
                if title_elem and snippet_elem:
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True)
                    
                    if title and url and snippet:
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet,
                            'label': title[:50] + '...' if len(title) > 50 else title,
                            'value': url,
                            'short_url': f"[{len(results)+1}]"
                        })
            except Exception as e:
                print(f"Error parsing search result: {e}")
                continue
        
        return results
        
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
    search_results = simple_web_search(search_query, max_results)
    
    if not search_results:
        return {
            "sources_gathered": [],
            "search_query": search_query,
            "web_research_result": f"No search results found for: {search_query}"
        }
    
    # Format results for LLM processing
    formatted_results = format_search_results_for_llm(search_results, search_query)
    
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
        
        # Create sources in the expected format
        sources_gathered = []
        for result in search_results:
            sources_gathered.append({
                'label': result['label'],
                'value': result['value'],
                'short_url': result['short_url']
            })
        
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