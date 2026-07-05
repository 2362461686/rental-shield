#!/bin/bash
set -e

# 首次启动：如果持久化卷里没有数据库，复制种子数据
if [ ! -f /app/data/rental.db ]; then
    echo ">>> 首次启动，初始化种子数据库..."
    cp /app/rental.db /app/data/rental.db
fi

# 保证后端读到持久化位置
export RENTAL_DB_PATH=/app/data/rental.db

echo ">>> 启动服务..."
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000
