# Gemini Fullstack LangGraph Quickstart - Multi-Provider Setup

This application now supports multiple AI providers: **Gemini** and **Ollama**.

## Quick Start

1. **Start the application:**
   ```bash
   .\start-app.bat
   ```

2. **Access the application:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:2024

## Provider Configuration

### Gemini (Google AI)
- **Required:** `GEMINI_API_KEY`
- **Get API Key:** https://aistudio.google.com/app/apikey
- **Models:** Gemini 2.0 Flash, Gemini 1.5 Flash, Gemini 1.5 Pro

### Ollama (Local AI)
- **Required:** Ollama running locally
- **Install Ollama:** https://ollama.ai/
- **Default URL:** http://localhost:11434
- **Models:** Llama 3.1, Gemma 3, Qwen 2.5, Mistral 7B

## Environment Setup

Create a `.env` file in the `backend` directory:

```env
# Gemini Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Ollama Configuration (optional)
OLLAMA_BASE_URL=http://localhost:11434

# Smithery.ai MCP Integration (Optional)
# Required to access and use MCP servers from the Smithery.ai registry.
# If not provided, the MCP integration feature will be disabled (server list will be empty).
SMITHERY_API_KEY=your_smithery_api_key_here
```

## Using Ollama

1. **Install Ollama:**
   - Download from https://ollama.ai/
   - Follow installation instructions for your OS

2. **Pull a model:**
   ```bash
   ollama pull llama3.1:8b
   ```

3. **Start Ollama:**
   ```bash
   ollama serve
   ```

4. **Select Ollama in the UI:**
   - Open the application
   - Choose "Ollama" from the AI Provider dropdown
   - Select your preferred model

## Features

- **Multi-Provider Support:** Switch between Gemini and Ollama
- **Free Search:** Uses DuckDuckGo search (no API key required)
- **Local Privacy:** Ollama runs entirely on your machine
- **Effort Levels:** Low, Medium, High research depth
- **Real-time Streaming:** See research progress in real-time

## Troubleshooting

### Backend Issues
- Ensure Python 3.11+ is installed
- Run `pip install -e .` in the backend directory
- Check that all imports are working

### Frontend Issues
- Ensure Node.js is installed
- Run `npm install` in the frontend directory
- Check that Vite is available

### Ollama Issues
- Verify Ollama is running: `ollama list`
- Check the base URL in your .env file
- Ensure the selected model is downloaded

### API Key Issues
- Verify your Gemini API key is correct
- Check that the .env file is in the backend directory
- Restart the backend after adding API keys

## Windows Compatibility

This application includes Windows-specific fixes:
- ✅ Windows batch files for easy startup
- ✅ Cross-platform Vite configuration
- ✅ PowerShell-compatible commands
- ✅ Proper path handling for Windows

## Architecture

- **Backend:** FastAPI + LangGraph + LangChain
- **Frontend:** React + Vite + TypeScript + Tailwind CSS
- **Search:** DuckDuckGo (free, no API key required)
- **Providers:** Gemini, Ollama (extensible to OpenAI, Anthropic, etc.) 