@echo off
chcp 65001 >nul
echo ========================================
echo 就业推荐系统 - 启动脚本
echo 作者: 刘怀仁
echo ========================================
echo.

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未安装Python，请先安装Python 3.10+
    pause
    exit /b 1
)

:: 进入后端目录
cd backend

:: 检查虚拟环境
if not exist "venv" (
    echo [1/5] 创建虚拟环境...
    python -m venv venv
)

:: 激活虚拟环境
call venv\Scripts\activate.bat

:: 检查依赖
echo [2/5] 安装依赖...
pip install -r requirements.txt -q

:: 数据库迁移
echo [3/5] 数据库迁移...
python manage.py makemigrations --noinput
python manage.py migrate --noinput

:: 检查是否需要创建管理员
python -c "from django.contrib.auth import get_user_model; User = get_user_model(); exit(0 if User.objects.filter(is_superuser=True).exists() else 1)" 2>nul
if errorlevel 1 (
    echo [4/5] 创建管理员账号...
    echo 请输入管理员信息:
    python manage.py createsuperuser
) else (
    echo [4/5] 管理员账号已存在，跳过
)

:: 启动服务器
echo [5/5] 启动服务器...
echo.
echo ========================================
echo 后端服务启动成功!
echo 地址: http://localhost:8000
echo 管理后台: http://localhost:8000/admin
echo API文档: http://localhost:8000/api/docs
echo ========================================
echo.
python manage.py runserver
