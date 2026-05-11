@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ===============================================
echo   道路裂缝检测 Web应用启动脚本
echo ===============================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo ✓ Python已安装

REM 检查requirements.txt
if not exist "requirements.txt" (
    echo ✗ requirements.txt 不存在
    pause
    exit /b 1
)

echo.
echo 正在检查/安装依赖...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo ✗ 安装依赖失败
    pause
    exit /b 1
)

echo ✓ 依赖已就绪

REM 验证配置
echo.
echo 正在验证模型配置...
python config_matcher.py
if errorlevel 1 (
    echo.
    echo ⚠ 警告：配置验证失败，但继续启动
)

REM 启动应用
echo.
echo ===============================================
echo   启动Web服务器...
echo ===============================================
echo.
echo 访问地址: http://localhost:5000
echo 按 Ctrl+C 停止服务器
echo.
echo ===============================================

python app.py
