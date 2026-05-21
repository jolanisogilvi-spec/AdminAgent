#!/bin/bash

# 后端服务启动脚本

set -e

echo "=== Admin Agent Backend Setup ==="

# 检查 Python 版本
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "Python version: $(python3 --version)"

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "Activating virtual environment..."
source venv/bin/activate

# 安装依赖
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "Please update .env with your actual configuration!"
fi

# 启动 Docker 服务（PostgreSQL + Redis）
echo "Starting database and Redis..."
cd ..
docker-compose up -d postgres redis
cd backend

# 等待数据库就绪
echo "Waiting for database to be ready..."
sleep 5

# 运行数据库迁移（如果有）
if [ -d "alembic" ]; then
    echo "Running database migrations..."
    alembic upgrade head
fi

# 启动应用
echo "Starting FastAPI application..."
echo "API Docs: http://localhost:8030/docs"
echo "Health Check: http://localhost:8030/health"
echo ""
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8030
