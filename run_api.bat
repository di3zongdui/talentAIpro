@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
"C:\Users\George Guo\.workbuddy\binaries\python\versions\3.13.12\python.exe" -X utf8 TalentAI_Pro\api\consultant_api.py
pause