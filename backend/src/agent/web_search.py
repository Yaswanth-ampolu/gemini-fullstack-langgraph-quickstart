"""Simple web search implementation for fallback when Google Search API is not available."""

import asyncio
from typing import List, Dict, Any
import time
import logging
import random
import aiohttp
from urllib.parse import quote_plus

# Add module-level variables for rate limiting
_last_image_call = 0.0
_IMAGE_RATE_INTERVAL = 2.0  # Increased to 2 seconds

# User-Agent rotation for avoiding detection
_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 Edg/95.0.1020.44",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
]


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


async def search_images(query: str, max_images: int = 8) -> List[Dict[str, Any]]:
    """
    Search for images related to the query using either DuckDuckGo or a fallback method.
    
    Args:
        query: Search query string
        max_images: Maximum number of images to return
        
    Returns:
        List of image results with url, title, and source
    """
    global _last_image_call
    
    print(f"🖼️ Searching for images: {query}")
    
    # Apply rate limiting with jitter
    current_time = time.time()
    time_since_last_call = current_time - _last_image_call
    
    if time_since_last_call < _IMAGE_RATE_INTERVAL:
        sleep_time = _IMAGE_RATE_INTERVAL - time_since_last_call + random.uniform(0.1, 0.5)  # Add jitter
        await asyncio.sleep(sleep_time)
        
    # Update last call timestamp
    _last_image_call = time.time()
    
    # Try primary method (DuckDuckGo) first
    images = await _duckduckgo_images(query, max_images)
    
    # If no images found, try the fallback method
    if not images:
        print(f"⚠️ DuckDuckGo image search failed, trying fallback method for: {query}")
        images = await _alternative_image_search(query, max_images)
    
    print(f"✅ Found {len(images)} images for: {query}")
    return images


async def _duckduckgo_images(query: str, max_images: int = 8) -> List[Dict[str, Any]]:
    """
    Search for images using DuckDuckGo with improved retry logic.
    """
    try:
        from duckduckgo_search import DDGS
        
        # Retry logic for rate limiting and temporary errors
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # Select a random user agent to avoid detection
                user_agent = random.choice(_USER_AGENTS)
                
                # Use asyncio.to_thread to run the blocking DuckDuckGo image search
                image_results = await asyncio.to_thread(
                    lambda: list(DDGS(headers={"User-Agent": user_agent}).images(query, max_results=max_images))
                )
                
                images = []
                for i, result in enumerate(image_results):
                    image_url = result.get('image', '')
                    title = result.get('title', f'Image {i+1}')
                    source = result.get('source', 'Unknown')
                    
                    # Validate image URL
                    if image_url and image_url.startswith(('http://', 'https://')):
                        images.append({
                            'url': image_url,
                            'title': title,
                            'source': source,
                            'alt': title[:100]  # Limit alt text length
                        })
                
                # If we got here without exception, break the retry loop
                if images:
                    return images
                else:
                    print(f"No images found on attempt {attempt+1}/{max_retries}, retrying...")
                    await asyncio.sleep(1 + attempt)  # Increasing delay between attempts
                
            except Exception as e:
                error_msg = str(e).lower()
                if "403" in error_msg or "ratelimit" in error_msg or "forbidden" in error_msg:
                    if attempt < max_retries - 1:  # Don't sleep on the last attempt
                        backoff_time = 2 ** attempt + random.uniform(0.5, 1.5)  # Add jitter to backoff
                        print(f"Rate limit hit, retrying in {backoff_time:.1f}s (attempt {attempt+1}/{max_retries})")
                        await asyncio.sleep(backoff_time)
                    continue
                else:
                    print(f"DuckDuckGo image search error: {e}")
                    break  # Try the alternative method instead
        
        return []
        
    except ImportError:
        print("Error: duckduckgo_search is not installed for image search")
        return []
    except Exception as e:
        print(f"Error in DuckDuckGo image search: {e}")
        return []


async def _alternative_image_search(query: str, max_images: int = 8) -> List[Dict[str, Any]]:
    """
    Alternative image search using a different approach when DuckDuckGo fails.
    This uses a simple scraping approach of public image search results.
    """
    try:
        # Using Unsplash API (no API key required for limited usage)
        encoded_query = quote_plus(query)
        url = f"https://unsplash.com/napi/search/photos?query={encoded_query}&per_page={max_images}"
        
        headers = {
            "User-Agent": random.choice(_USER_AGENTS),
            "Accept": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    try:
                        data = await response.json()
                        results = data.get("results", [])
                        
                        images = []
                        for i, result in enumerate(results[:max_images]):
                            image_url = result.get("urls", {}).get("regular", "")
                            title = result.get("description", f"Image {i+1}") or f"Image {i+1}"
                            source = "Unsplash"
                            user = result.get("user", {}).get("name", "Unknown")
                            
                            # Validate image URL
                            if image_url and image_url.startswith(('http://', 'https://')):
                                images.append({
                                    'url': image_url,
                                    'title': title,
                                    'source': f"{source} - {user}",
                                    'alt': title[:100]  # Limit alt text length
                                })
                        
                        return images
                    except Exception as e:
                        print(f"Error parsing Unsplash results: {e}")
                        return []
                else:
                    print(f"Unsplash API returned status code: {response.status}")
                    return []
                
    except Exception as e:
        print(f"Alternative image search failed: {e}")
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
    max_results: int = 5,
    include_images: bool = True,
    max_images: int = 6
) -> Dict[str, Any]:
    """
    Perform web search and process results with LLM, optionally including images.
    
    Args:
        search_query: The search query
        llm: The LLM instance to process results
        search_prompt_template: Template for the search prompt
        max_results: Maximum number of search results
        include_images: Whether to include image search
        max_images: Maximum number of images to search for
        
    Returns:
        Dictionary with processed search results and images
    """
    # Perform both text and image searches concurrently
    if include_images:
        search_results, image_results = await asyncio.gather(
            simple_web_search(search_query, max_results),
            search_images(search_query, max_images),
            return_exceptions=True
        )
        
        # Handle exceptions from concurrent operations
        if isinstance(search_results, Exception):
            print(f"Text search failed: {search_results}")
            search_results = []
            
        if isinstance(image_results, Exception):
            print(f"Image search failed: {image_results}")
            image_results = []
    else:
        search_results = await simple_web_search(search_query, max_results)
        image_results = []
    
    if not search_results and not image_results:
        return {
            "sources_gathered": [],
            "search_query": search_query,
            "web_research_result": f"No search results found for: {search_query}",
            "images": []
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
            "web_research_result": processed_content,
            "images": image_results
        }
        
    except Exception as e:
        print(f"Error processing search results with LLM: {e}")
        return {
            "sources_gathered": sources_gathered,
            "search_query": search_query,
            "web_research_result": formatted_results,
            "images": image_results
        } 