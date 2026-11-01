@echo off
title Demon-Devil Local Dashboard & Auth Server
cd /d "%~dp0"
echo ========================================================
echo   Starting Demon-Devil Local Dashboard & Auth Server
echo ========================================================
start http://localhost:8080
python server.py
pause
