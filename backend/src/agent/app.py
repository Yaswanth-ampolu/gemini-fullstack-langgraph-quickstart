# mypy: disable - error - code = "no-untyped-def,misc"
import pathlib
import os
import aiohttp
import asyncio
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import fastapi.exceptions
from typing import Dict, List, Any, Optional
from agent.models import get_supported_models
from .mcp_registry import fetch_mcp_servers, get_mcp_server_details
from .tools_and_schemas import McpServerInfo

# Define the FastAPI app
app = FastAPI()

@app.get("/api/providers")
async def get_available_providers() -> List[Dict[str, Any]]:
    """
    Get available LLM providers based on environment configuration.
    Returns providers that have their API keys configured or are accessible.
    """
    available_providers = []
    supported_models = get_supported_models()

    # Check Gemini availability
    if os.getenv("GEMINI_API_KEY"):
        available_providers.append({
            "provider": "gemini",
            "models": supported_models.get("gemini", [])
        })

    # Check if Ollama is available by trying to connect to it
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f"{ollama_base_url}/api/tags") as response:
                if response.status == 200:
                    available_providers.append({
                        "provider": "ollama",
                        "models": supported_models.get("ollama", [])
                    })
    except (aiohttp.ClientError, asyncio.TimeoutError):
        # Ollama is not accessible, skip it
        pass

    return available_providers

@app.get("/api/mcp/servers", response_model=List[McpServerInfo])
async def list_mcp_servers():
    """
    Fetches and returns a list of available MCP servers.
    """
    try:
        raw_servers = fetch_mcp_servers() # This is a synchronous call
        if not raw_servers: # Assuming fetch_mcp_servers returns None or [] on error or no key
            # If SMITHERY_API_KEY was not set, fetch_mcp_servers prints a warning and returns []
            # If there was a request error, it also prints a message and returns []
            # So, an empty list here could mean no servers found, or an issue fetching.
            # For now, we return empty list, client can decide how to interpret.
            return []

        mcp_servers = []
        for server_data in raw_servers:
            # Basic mapping, assuming structure from Smithery registry
            # Tools might need more complex parsing if not a simple list of strings
            tools_list = server_data.get("tools", [])
            if isinstance(tools_list, list) and all(isinstance(t, str) for t in tools_list):
                pass # Already in correct format
            elif isinstance(tools_list, list) and all(isinstance(t, dict) for t in tools_list):
                 # If tools are dicts, e.g. [{"name": "tool1"}, {"name": "tool2"}], extract names
                tools_list = [t.get("name") for t in tools_list if t.get("name")]
            else: # Fallback or if structure is unknown/unexpected
                tools_list = []


            mcp_servers.append(McpServerInfo(
                qualified_name=server_data.get("qualifiedName", server_data.get("qualified_name")), # Handle potential casing
                display_name=server_data.get("displayName", server_data.get("display_name")),
                description=server_data.get("description", ""),
                tools=tools_list,
                config_schema=server_data.get("configSchema", server_data.get("config_schema", {})),
            ))
        return mcp_servers
    except Exception as e:
        # Log the exception e for server-side observability
        print(f"Error processing /api/mcp/servers: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch or process MCP server information.")

@app.get("/api/mcp/servers/{qualified_name}", response_model=McpServerInfo)
async def get_single_mcp_server(qualified_name: str):
    """
    Fetches and returns details for a specific MCP server.
    """
    try:
        server_details = get_mcp_server_details(qualified_name) # Synchronous call
        if not server_details:
            # get_mcp_server_details returns None if API key missing or HTTP error
            raise HTTPException(status_code=404, detail=f"MCP Server '{qualified_name}' not found or error fetching details.")

        # Similar mapping as in list_mcp_servers
        tools_list = server_details.get("tools", [])
        if isinstance(tools_list, list) and all(isinstance(t, str) for t in tools_list):
            pass
        elif isinstance(tools_list, list) and all(isinstance(t, dict) for t in tools_list):
            tools_list = [t.get("name") for t in tools_list if t.get("name")]
        else:
            tools_list = []

        return McpServerInfo(
            qualified_name=server_details.get("qualifiedName", server_details.get("qualified_name")),
            display_name=server_details.get("displayName", server_details.get("display_name")),
            description=server_details.get("description", ""),
            tools=tools_list,
            config_schema=server_details.get("configSchema", server_details.get("config_schema", {})),
        )
    except HTTPException: # Re-raise HTTPException directly
        raise
    except Exception as e:
        print(f"Error processing /api/mcp/servers/{qualified_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch or process MCP server details.")


def create_frontend_router(build_dir="../frontend/dist"):
    """Creates a router to serve the React frontend.

    Args:
        build_dir: Path to the React build directory relative to this file.

    Returns:
        A Starlette application serving the frontend.
    """
    build_path = pathlib.Path(__file__).parent.parent.parent / build_dir
    static_files_path = build_path / "assets"  # Vite uses 'assets' subdir

    if not build_path.is_dir() or not (build_path / "index.html").is_file():
        print(
            f"WARN: Frontend build directory not found or incomplete at {build_path}. Serving frontend will likely fail."
        )
        # Return a dummy router if build isn't ready
        from starlette.routing import Route

        async def dummy_frontend(request):
            return Response(
                "Frontend not built. Run 'npm run build' in the frontend directory.",
                media_type="text/plain",
                status_code=503,
            )

        return Route("/{path:path}", endpoint=dummy_frontend)

    build_dir = pathlib.Path(build_dir)

    react = FastAPI(openapi_url="")
    react.mount(
        "/assets", StaticFiles(directory=static_files_path), name="static_assets"
    )

    @react.get("/{path:path}")
    async def handle_catch_all(request: Request, path: str):
        fp = build_path / path
        if not fp.exists() or not fp.is_file():
            fp = build_path / "index.html"
        return fastapi.responses.FileResponse(fp)

    return react


# Mount the frontend under /app to not conflict with the LangGraph API routes
app.mount(
    "/app",
    create_frontend_router(),
    name="frontend",
)
