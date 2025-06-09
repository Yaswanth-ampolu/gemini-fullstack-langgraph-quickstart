# mypy: disable - error - code = "no-untyped-def,misc"
import pathlib
import os
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import fastapi.exceptions
from typing import Dict, List, Any
from agent.models import get_supported_models, check_provider_availability

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
    provider_availability = check_provider_availability()

    for provider, is_available in provider_availability.items():
        if is_available:
            available_providers.append({
                "provider": provider,
                "models": supported_models.get(provider, [])
            })

    return available_providers


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
