@echo off
cd /d "%~dp0TalentAI_Pro"
set PYTHONPATH=%~dp0TalentAI_Pro
echo Starting TalentAI Pro API Server v2.0...
echo.
echo API Docs: http://localhost:8089/docs
echo LLM Config: frontend/llm_config.html
echo.
python api\server.py
