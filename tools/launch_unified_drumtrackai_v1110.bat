@echo off
echo ===============================================
echo    DrumTracKAI v1.1.10 Unified System Launcher
echo ===============================================
echo.
echo Starting all DrumTracKAI components:
echo - Frontend (React on port 3001)
echo - Backend (FastAPI on port 8000) 
echo - Admin App (PySide6 with Expert Model)
echo.

REM Set the project directory
set PROJECT_DIR=D:\DrumTracKAI_v1.1.10
cd /d "%PROJECT_DIR%"

echo [1/3] Starting Backend API Server...
start "DrumTracKAI Backend" cmd /k "call drumtrackai_env\Scripts\activate && python drumtrackai_api_server_clean.py"

echo [2/3] Starting Frontend React App...
cd web-frontend
start "DrumTracKAI Frontend" cmd /k "npm start"
cd ..

echo [3/3] Starting Admin App...
start "DrumTracKAI Admin" cmd /k "call drumtrackai_env\Scripts\activate && python drumtrackai_admin_analyzer.py"

echo.
echo ===============================================
echo All DrumTracKAI v1.1.10 components started!
echo.
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000
echo Admin App: Desktop application window
echo.
echo Expert Model: 88.7%% Sophistication
echo Three-Tier System: Basic, Advanced, Professional
echo ===============================================
echo.
pause
