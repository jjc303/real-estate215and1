@echo off
chcp 65001 >nul
title 房地产租赁平台 - 启动
set "PROJECT_ROOT=%~dp0"

echo ========================================
echo   房地产租赁平台 - 启动中...
echo ========================================
echo.

REM ========== 检测是否已有服务在运行 ==========
docker ps --format "{{.Names}}" 2>nul | findstr /R "^rent_mysql$ ^rent_backend$ ^ai-engine$" >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] 检测到服务容器已在运行！
    echo [INFO] 如需重启，请先运行 stop.bat 关闭所有服务
    echo.
    echo   前端:    http://localhost:5173
    echo   后端:    http://localhost:8000
    echo   AI引擎:  http://localhost:9000
    echo.
    pause
    exit /b 0
)
netstat -ano 2>nul | findstr ":5173 " | findstr LISTENING >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] 检测到前端已在运行（端口 5173 已被占用）
    echo [INFO] 如需重启，请先运行 stop.bat 关闭所有服务
    echo.
    echo   前端:    http://localhost:5173
    echo.
    pause
    exit /b 0
)

REM ========== 检查 / 启动 Docker Desktop ==========
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Docker Desktop 未运行，正在启动中...
    if exist "C:\Program Files\Docker\Docker\Docker Desktop.exe" (
        start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    )
    echo [INFO] 等待 Docker Desktop 就绪（最长 90 秒）...
    set /a docker_wait=0
    :wait_docker
    timeout /t 3 >nul
    set /a docker_wait+=3
    docker info >nul 2>&1
    if %errorlevel% equ 0 goto docker_ok
    if %docker_wait% lss 90 goto wait_docker
    echo [ERROR] Docker Desktop 启动超时，请手动启动后重试
    pause
    exit /b 1
    :docker_ok
    echo [INFO] Docker Desktop 已就绪
)

REM ========== 清理旧容器（确保环境变量重新加载）==========
echo.
echo [INFO] 清理旧容器 ...
cd /d "%PROJECT_ROOT%deploy"
docker compose down >nul 2>&1
cd /d "%PROJECT_ROOT%ai-engine"
docker compose down >nul 2>&1

REM ========== 创建缺失的配置文件（已有则跳过）==========
if not exist "%PROJECT_ROOT%deploy\.env" (
    echo [INFO] 创建 deploy\.env
    copy "%PROJECT_ROOT%deploy\.env.example" "%PROJECT_ROOT%deploy\.env" >nul
)
if not exist "%PROJECT_ROOT%ai-engine\.env" (
    echo [INFO] 创建 ai-engine\.env
    copy "%PROJECT_ROOT%ai-engine\.env.example" "%PROJECT_ROOT%ai-engine\.env" >nul
)
if not exist "%PROJECT_ROOT%ai-engine\config\local.env" (
    echo [INFO] 创建 ai-engine\config\local.env
    copy "%PROJECT_ROOT%ai-engine\config\local.env.example" "%PROJECT_ROOT%ai-engine\config\local.env" >nul
)

REM ========== 启动 MySQL ==========
echo.
echo [INFO] 启动 MySQL ...
cd /d "%PROJECT_ROOT%deploy"
docker compose up -d mysql
if %errorlevel% neq 0 (
    echo [ERROR] MySQL 启动失败！
    pause
    exit /b 1
)

REM ========== 等待 MySQL 健康 ==========
echo [INFO] 等待 MySQL 就绪（最长 90 秒）...
set /a count=0
:wait_mysql
timeout /t 3 >nul
set /a count+=3
docker inspect -f "{{.State.Health.Status}}" rent_mysql 2>nul | findstr "healthy" >nul
if %errorlevel% equ 0 goto mysql_ok
if %count% lss 90 goto wait_mysql
echo [WARN] MySQL 健康检查超时，继续启动后续服务...

:mysql_ok
echo [INFO] MySQL 已就绪

REM ========== 启动 AI 引擎 ==========
echo.
echo [INFO] 启动 AI 引擎 ...
cd /d "%PROJECT_ROOT%ai-engine"
docker compose up -d
if %errorlevel% neq 0 (
    echo [WARN] AI 引擎启动失败，请检查 ai-engine 配置
)

REM ========== 等待 AI 引擎就绪 ==========
echo [INFO] 等待 AI 引擎就绪（最长 60 秒）...
set /a ai_wait=0
:wait_ai
timeout /t 3 >nul
set /a ai_wait+=3
curl -sf http://127.0.0.1:9000/docs >nul 2>&1
if %errorlevel% equ 0 goto ai_ok
if %ai_wait% lss 60 goto wait_ai
echo [WARN] AI 引擎就绪检查超时，继续启动...

:ai_ok
echo [INFO] AI 引擎已就绪

REM ========== 启动后端 ==========
echo.
echo [INFO] 启动后端 ...
cd /d "%PROJECT_ROOT%deploy"
docker compose up -d backend
if %errorlevel% neq 0 (
    echo [ERROR] 后端启动失败！
    pause
    exit /b 1
)

REM ========== 等待后端就绪 ==========
echo [INFO] 等待后端就绪（最长 30 秒）...
set /a be_wait=0
:wait_backend
timeout /t 2 >nul
set /a be_wait+=2
curl -sf http://127.0.0.1:8000/api/v1/houses >nul 2>&1
if %errorlevel% equ 0 goto be_ok
if %be_wait% lss 30 goto wait_backend
echo [WARN] 后端就绪检查超时，继续执行数据库迁移...

:be_ok
echo [INFO] 后端已就绪

REM ========== 数据库迁移 ==========
echo.
echo [INFO] 执行数据库迁移...
docker exec rent_backend sh -c "cd //app//backend && alembic upgrade head" 2>&1

REM ========== 安装前端依赖（首次运行）==========
echo.
if not exist "%PROJECT_ROOT%frontend\node_modules" (
    echo [INFO] 首次运行，安装前端依赖（可能需要几分钟）...
    cd /d "%PROJECT_ROOT%frontend"
    call npm install
    if %errorlevel% neq 0 (
        echo [ERROR] 前端依赖安装失败！
        echo [INFO] 请确保已安装 Node.js：https://nodejs.org
        pause
        exit /b 1
    )
)

REM ========== 启动前端 ==========
echo [INFO] 启动前端 ...
cd /d "%PROJECT_ROOT%frontend"
start "房地产租赁-前端" cmd /c "cd /d "%PROJECT_ROOT%frontend" && npm run dev"

echo.
echo ========================================
echo   启动完成！
echo.
echo   前端:    http://localhost:5173
echo   后端:    http://localhost:8000
echo   AI引擎:  http://localhost:9000
echo.
echo   请访问 http://localhost:5173
echo ========================================
echo.
pause
