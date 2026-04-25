@echo off
cd /d "%~dp0TalentAI_Pro"
set PYTHONPATH=%~dp0TalentAI_Pro
echo Starting TalentAI Pro API Server...
echo.
echo Using Python: %PYTHONPATH%
echo.
echo Server will run at: http://localhost:8089
echo API Docs: http://localhost:8089/docs
echo.
echo Press Ctrl+C to stop the server.
echo.
"C:\Users\George Guo\.workbuddy\binaries\python\versions\3.13.12\python.exe" api/server.py
pause