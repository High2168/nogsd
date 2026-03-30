@echo off
chcp 65001 >nul
echo ========================================
echo 前端服务启动脚本
echo 作者: 刘怀仁
echo ========================================
echo.

:: 检查Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未安装Node.js，请先安装Node.js 18+
    pause
    exit /b 1
)

:: 进入前端目录
cd frontend

:: 检查node_modules
if not exist "node_modules" (
    echo [1/2] 安装依赖...
    npm install
) else (
    echo [1/2] 依赖已安装，跳过
)

:: 启动开发服务器
echo [2/2] 启动开发服务器...
echo.
echo ========================================
echo 前端服务启动成功!
echo 地址: http://localhost:3000
echo ========================================
echo.
npm run dev
