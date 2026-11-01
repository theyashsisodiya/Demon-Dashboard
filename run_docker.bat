@echo off
title Demon-Dashboard Docker Launcher
echo ========================================================
echo   Launching Demon-Dashboard via Docker
echo ========================================================
echo Checking Docker service...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed or not running in PATH!
    echo Please install Docker Desktop from https://www.docker.com/
    pause
    exit /b
)

echo Building and starting Demon-Dashboard container...
docker compose up -d --build
if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo   Demon-Dashboard is RUNNING in Docker!
    echo   URL: http://localhost:8080
    echo ========================================================
    echo.
    echo To view live logs: docker logs -f demon-dashboard
    echo To stop container: docker compose down
) else (
    echo.
    echo [ERROR] Failed to start Docker container.
)
pause
