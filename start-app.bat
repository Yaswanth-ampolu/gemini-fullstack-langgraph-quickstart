@echo off
echo Starting Gemini Fullstack LangGraph Application...
echo.

REM Check if Python is available
echo Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ and try again
    pause
    exit /b 1
)

REM Check if Node.js is available
echo Checking Node.js...
node --version
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js and try again
    pause
    exit /b 1
)

REM Check if npm is available
echo Checking npm...
npm --version
if errorlevel 1 (
    echo ERROR: npm is not installed or not in PATH
    echo Please install Node.js (which includes npm) and try again
    pause
    exit /b 1
)

echo.
echo All prerequisites found!
echo.

echo Setting up backend...
cd backend
if not exist "src\agent\__init__.py" (
    echo ERROR: Backend source files not found
    echo Please ensure you're in the correct directory
    pause
    exit /b 1
)

echo Installing backend dependencies...
pip install -e .
if errorlevel 1 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)

cd ..

echo Setting up frontend...
cd frontend
if not exist "package.json" (
    echo ERROR: Frontend package.json not found
    echo Please ensure you're in the correct directory
    pause
    exit /b 1
)

REM Check if node_modules exists, if not install dependencies
if not exist "node_modules" (
    echo Installing frontend dependencies...
    npm install
    if errorlevel 1 (
        echo ERROR: Failed to install frontend dependencies
        pause
        exit /b 1
    )
) else (
    echo Frontend dependencies already installed
)

cd ..

echo.
echo ========================================
echo Starting Backend Server (Port 2024)...
echo ========================================
echo.

REM Start backend in a new window
start "Backend Server" cmd /k "cd /d %cd%\backend && echo Starting LangGraph API server... && langgraph dev --host 0.0.0.0 --port 2024"

REM Wait a moment for backend to start
echo Waiting for backend to start...
timeout /t 5 /nobreak

echo.
echo ========================================
echo Starting Frontend Server (Port 5173)...
echo ========================================
echo.

REM Start frontend in a new window
start "Frontend Server" cmd /k "cd /d %cd%\frontend && echo Starting Vite development server... && npm run dev"

echo.
echo ========================================
echo Application Starting!
echo ========================================
echo.
echo Backend API: http://localhost:2024
echo Frontend UI: http://localhost:5173
echo.
echo Both servers are starting in separate windows.
echo Close those windows to stop the servers.
echo.
echo Note: Make sure you have set your API keys:
echo - GEMINI_API_KEY for Google Gemini
echo - OLLAMA_BASE_URL for Ollama (optional, defaults to http://localhost:11434)
echo.
echo For Ollama support, make sure Ollama is running locally.
echo.
pause 