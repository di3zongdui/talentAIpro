@echo off
REM TalentAI Pro - Deployment Script (Windows)
REM Usage: scripts\deploy.bat [production|staging|dev]

setlocal enabledelayedexpansion

set "PROJECT_NAME=TalentAI-Pro"
set "COMPOSE_FILE=docker-compose.yml"
set "TAG=%~1"
if "%TAG%"=="" set "TAG=latest"

echo === TalentAI Pro Deployment ===
echo Environment: %TAG%

REM Check Docker
docker version >nul 2>&1
if errorlevel 1 (
    echo Docker is required but not installed.
    exit /b 1
)

REM Check Docker Compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo Docker Compose is required but not installed.
    exit /b 1
)

REM Create directories
echo Creating directories...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "ssl" mkdir ssl

REM Load environment variables
if exist ".env" (
    echo Loading .env file...
    for /f "usebackq tokens=*" %%a in (.env) do (
        set "%%a"
    )
)

REM Build and deploy
echo Building Docker images...
docker-compose -f %COMPOSE_FILE% build --pull

echo Stopping existing containers...
docker-compose -f %COMPOSE_FILE% down

echo Starting services...
docker-compose -f %COMPOSE_FILE% up -d

REM Wait for services
echo Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Health check
echo Performing health check...
set "attempts=0"
:health_check
set /a attempts+=1
curl -sf http://localhost:8000/health >nul 2>&1
if not errorlevel 1 (
    echo API is healthy!
    goto :show_status
)
if %attempts% equ 30 (
    echo Health check failed. Checking logs...
    docker-compose -f %COMPOSE_FILE% logs api
    exit /b 1
)
echo Waiting for API... (!attempts!/30)
timeout /t 2 /nobreak >nul
goto :health_check

:show_status
echo.
echo === Deployment Complete ===
echo.
docker-compose -f %COMPOSE_FILE% ps
echo.
echo API: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo.
echo To view logs: docker-compose -f %COMPOSE_FILE% logs -f
echo To stop: docker-compose -f %COMPOSE_FILE% down

endlocal
