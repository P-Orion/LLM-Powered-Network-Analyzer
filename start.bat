@echo off
echo ========================================
echo   LLM Private Log Anomaly Finder
echo   PCAPNG Network Analysis Tool
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "backend\venv" (
    echo Creating Python virtual environment...
    cd backend
    python -m venv venv
    cd ..
)

REM Check if dependencies are installed
echo Checking dependencies...
cd backend
call venv\Scripts\activate
pip install -r requirements.txt >nul 2>&1
cd ..

REM Start Backend in a new window
echo [1/2] Starting Backend (FastAPI)...
start "Backend - FastAPI" cmd /k "cd backend && venv\Scripts\activate && python main.py"

REM Wait a few seconds for backend to start
timeout /t 5 /nobreak >nul

REM Start Frontend in a new window
echo [2/2] Starting Frontend (Angular)...
start "Frontend - Angular" cmd /k "cd frontend && ng serve"

echo.
echo ========================================
echo   Both servers are starting!
echo ========================================
echo.
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:4200
echo.
echo   IMPORTANT: This tool analyzes PCAPNG files only!
echo   Use Wireshark, tcpdump, or the test generator
echo   to create .pcapng files for analysis.
echo.
echo   Two terminal windows will open.
echo   Wait for both to finish loading, then
echo   open http://localhost:4200 in your browser.
echo.
echo   Press any key to open the browser...
pause >nul

REM Open browser to the application
start http://localhost:4200

echo.
echo   Application opened in browser!
echo   Upload .pcapng files to analyze network traffic.
echo   Keep the terminal windows open.
echo.
