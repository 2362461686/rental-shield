# ── Stage 1: 构建前端 ──
FROM node:18-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ── Stage 2: 运行后端 + 提供前端 ──
FROM python:3.11-slim
WORKDIR /app

# 系统依赖（pymysql 需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libmariadb-dev && \
    rm -rf /var/lib/apt/lists/*

# Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 后端源码
COPY backend/ ./backend/

# 根目录遗留模块（agents.py 等依��）
COPY config.py agents.py db.py utils.py seed_data.py ./

# 种子数据库
COPY rental.db ./

# 前端构建产物
COPY --from=frontend /app/frontend/dist/ ./frontend/dist/

# 数据持久化目录
RUN mkdir -p /app/data images

# 启动脚本
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
