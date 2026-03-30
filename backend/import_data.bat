@echo off
chcp 65001 >nul
echo ========================================
echo 导入职位数据
echo ========================================
echo.

:: 设置CSV文件路径
set CSV_PATH=path\to\job_posts.csv

:: 检查文件是否存在
if not exist "%CSV_PATH%" (
    echo [错误] CSV文件不存在: %CSV_PATH%
    echo 请修改脚本中的CSV_PATH变量为实际路径
    pause
    exit /b 1
)

:: 进入后端目录
cd backend

:: 激活虚拟环境
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

:: 运行导入命令
echo 开始导入数据...
echo.
python manage.py shell -c "from apps.data.import_data import import_data; import_data(r'%CSV_PATH%', limit=2000, create_users=True)"

echo.
echo ========================================
echo 数据导入完成!
echo ========================================
pause
