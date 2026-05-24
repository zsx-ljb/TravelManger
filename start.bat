@echo off
chcp 65001 >nul

echo ===================================
echo     旅行规划助手 - 启动脚本
echo ===================================

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

:: 检查依赖
echo.
echo 检查依赖...
pip list | findstr "streamlit fastapi langchain" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖...
    pip install -r requirements.txt
)

:: 创建数据目录
if not exist data mkdir data

:: 选择启动模式
echo.
echo 请选择启动模式:
echo 1. 启动Web界面 (Streamlit)
echo 2. 启动API服务 (FastAPI)
echo 3. 同时启动
echo 4. 运行测试
set /p choice=请输入选项 (1-4):

if "%choice%"=="1" (
    echo.
    echo 启动Web界面...
    echo 访问地址: http://localhost:8501
    cd frontend && streamlit run app.py
) else if "%choice%"=="2" (
    echo.
    echo 启动API服务...
    echo API地址: http://localhost:8000
    echo API文档: http://localhost:8000/docs
    python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
) else if "%choice%"=="3" (
    echo.
    echo 同时启动Web界面和API服务...
    echo Web界面: http://localhost:8501
    echo API服务: http://localhost:8000
    start "API服务" python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
    timeout /t 3 /nobreak >nul
    cd frontend && streamlit run app.py
) else if "%choice%"=="4" (
    echo.
    echo 运行测试...
    python -m pytest tests/ -v
) else (
    echo 无效选项
)

pause
