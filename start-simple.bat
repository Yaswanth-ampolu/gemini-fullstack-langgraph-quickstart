@echo off
echo Starting Gemini Fullstack LangGraph Application...
echo.

echo Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)

echo Checking Node.js...
node --version
if errorlevel 1 (
    echo ERROR: Node.js not found
    pause
    exit /b 1
)

echo All prerequisites found!
echo.

echo Installing backend...
cd backend
pip install -e .
cd ..

echo Installing frontend...
cd frontend
if not exist "node_modules" (
    npm install
)
cd ..

echo Starting servers...
start "Backend" cmd /k "cd backend && langgraph dev --host 0.0.0.0 --port 2024"
timeout /t 3
start "Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Servers starting in separate windows!
echo Backend: http://localhost:2024
echo Frontend: http://localhost:5173
echo.
pause 