"""Model utility functions for different LLM providers."""

import os
from typing import Any, Dict, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama


def get_llm(model_name: str, provider: str = "gemini", **kwargs) -> Any:
    """
    Get an LLM instance based on the provider and model name.

    Args:
        model_name: The name of the model to use
        provider: The provider ('gemini' or 'ollama'). Defaults to 'gemini'
        **kwargs: Additional arguments to pass to the LLM constructor

    Returns:
        An LLM instance for the specified provider

    Raises:
        ValueError: If the provider is not supported or API key is missing
    """
    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set")

        return ChatGoogleGenerativeAI(
            model=model_name,
            api_key=api_key,
            **kwargs
        )

    elif provider == "ollama":
        # Ollama typically runs locally and doesn't require an API key
        # Get the base URL from environment variable, default to localhost
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

        return ChatOllama(
            model=model_name,
            base_url=base_url,
            **kwargs
        )

    else:
        raise ValueError(f"Unsupported provider: {provider}. Supported providers: gemini, ollama")


def get_supported_models() -> Dict[str, list]:
    """
    Get default model names for each provider.

    Returns:
        Dictionary mapping providers to their default models
    """
    return {
        "gemini": [
            {
                "name": "gemini-2.0-flash-exp",
                "displayName": "Gemini 2.0 Flash",
            },
            {
                "name": "gemini-1.5-flash",
                "displayName": "Gemini 1.5 Flash",
            },
            {
                "name": "gemini-1.5-pro",
                "displayName": "Gemini 1.5 Pro",
            }
        ],
        "ollama": [
            {
                "name": "llama3.1:8b",
                "displayName": "Llama 3.1 8B",
            },
            {
                "name": "gemma3:4b",
                "displayName": "Gemma 3 4B",
            },
            {
                "name": "qwen2.5:7b",
                "displayName": "Qwen 2.5 7B",
            },
            {
                "name": "mistral:7b",
                "displayName": "Mistral 7B",
            }
        ]
    }


def check_provider_availability() -> Dict[str, bool]:
    """
    Check which providers are available based on environment configuration.
    
    Returns:
        Dictionary mapping provider names to their availability status
    """
    availability = {}
    
    # Check Gemini - only available if API key is set
    gemini_key = os.getenv("GEMINI_API_KEY")
    availability["gemini"] = bool(gemini_key)
    
    # Check Ollama by attempting to connect
    try:
        import requests
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        response = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
        availability["ollama"] = response.status_code == 200
    except Exception:
        availability["ollama"] = False
    
    return availability 