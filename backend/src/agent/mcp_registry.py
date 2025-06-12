import os
import requests
from typing import List, Dict, Any, Optional

SMITHERY_REGISTRY_BASE_URL = "https://registry.smithery.ai"

def fetch_mcp_servers() -> List[Dict[str, Any]]:
    """
    Fetches the list of available MCP servers from the Smithery registry.
    """
    api_key = os.getenv("SMITHERY_API_KEY")
    if not api_key:
        print("Warning: SMITHERY_API_KEY environment variable not set. Cannot fetch MCP servers.")
        return []

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    try:
        response = requests.get(f"{SMITHERY_REGISTRY_BASE_URL}/servers", headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching MCP servers: {e}")
        return []

def get_mcp_server_details(qualified_name: str) -> Optional[Dict[str, Any]]:
    """
    Fetches the details for a specific MCP server from the Smithery registry.
    """
    api_key = os.getenv("SMITHERY_API_KEY")
    if not api_key:
        print(f"Warning: SMITHERY_API_KEY environment variable not set. Cannot fetch details for {qualified_name}.")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    try:
        response = requests.get(f"{SMITHERY_REGISTRY_BASE_URL}/servers/{qualified_name}", headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching MCP server details for {qualified_name}: {e}")
        return None

if __name__ == '__main__':
    # Example usage (requires SMITHERY_API_KEY to be set)
    print("Fetching MCP servers...")
    servers = fetch_mcp_servers()
    if servers:
        print(f"Found {len(servers)} servers.")
        for server in servers:
            print(f"  - {server.get('qualified_name')}: {server.get('display_name')}")

        # Fetch details for the first server found
        if servers[0].get('qualified_name'):
            qname = servers[0]['qualified_name']
            print(f"\nFetching details for {qname}...")
            details = get_mcp_server_details(qname)
            if details:
                print(f"Details for {qname}:")
                for key, value in details.items():
                    print(f"  {key}: {value}")
            else:
                print(f"Could not fetch details for {qname}.")
    else:
        print("No MCP servers found or error fetching them.")
