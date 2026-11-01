@echo off
title Demon-Devil Cloudflare Tunnel
echo ========================================================
echo   Starting Cloudflare Tunnel to Local Server (Port 8080)
echo ========================================================
echo Copy the generated https://*.trycloudflare.com URL
echo and you can place it in /sdcard/Download/server_url.txt
echo on your phone for instant SSL authentication!
echo ========================================================
C:\cloudflared\cloudflared.exe tunnel --url http://localhost:8080
pause
