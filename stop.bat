@echo off
chcp 65001 >nul
title 房地产租赁平台 - 关闭
set "PROJECT_ROOT=%~dp0"

echo ========================================
echo   房地产租赁平台 - 关闭中...
echo ========================================
echo.

REM ========== 关闭前端（释放 5173/5174 端口）==========
echo [INFO] 关闭前端 ...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do (
    taskkill /f /pid %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5174 ^| findstr LISTENING') do (
    taskkill /f /pid %%a >nul 2>&1
)
taskkill /f /fi "WINDOWTITLE eq 房地产租赁-前端*" >nul 2>&1
echo [INFO] 前端已关闭

REM ========== 关闭后端 + MySQL ==========
echo [INFO] 关闭后端和 MySQL ...
cd /d "%PROJECT_ROOT%deploy"
docker compose down
echo [INFO] 后端和 MySQL 已关闭

REM ========== 关闭 AI 引擎 ==========
echo [INFO] 关闭 AI 引擎 ...
cd /d "%PROJECT_ROOT%ai-engine"
docker compose down
echo [INFO] AI 引擎已关闭

echo.
echo ========================================
echo   所有服务已关闭
echo   下次使用请运行 start.bat
echo ========================================
echo.
pause
