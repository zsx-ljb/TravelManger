#!/bin/bash

# 旅行规划助手启动脚本

echo "==================================="
echo "    旅行规划助手 - 启动脚本"
echo "==================================="

# 检查Python版本
python_version=$(python --version 2>&1)
echo "Python版本: $python_version"

# 检查是否安装了依赖
echo ""
echo "检查依赖..."
pip list | grep -E "streamlit|fastapi|langchain" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "正在安装依赖..."
    pip install -r requirements.txt
fi

# 创建数据目录
mkdir -p data

# 选择启动模式
echo ""
echo "请选择启动模式:"
echo "1. 启动Web界面 (Streamlit)"
echo "2. 启动API服务 (FastAPI)"
echo "3. 同时启动"
echo "4. 运行测试"
read -p "请输入选项 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "启动Web界面..."
        echo "访问地址: http://localhost:8501"
        cd frontend && streamlit run app.py
        ;;
    2)
        echo ""
        echo "启动API服务..."
        echo "API地址: http://localhost:8000"
        echo "API文档: http://localhost:8000/docs"
        python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
        ;;
    3)
        echo ""
        echo "同时启动Web界面和API服务..."
        echo "Web界面: http://localhost:8501"
        echo "API服务: http://localhost:8000"

        # 后台启动API服务
        python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload &
        API_PID=$!

        # 等待API服务启动
        sleep 3

        # 启动Web界面
        cd frontend && streamlit run app.py

        # 清理
        kill $API_PID 2>/dev/null
        ;;
    4)
        echo ""
        echo "运行测试..."
        python -m pytest tests/ -v
        ;;
    *)
        echo "无效选项"
        exit 1
        ;;
esac
