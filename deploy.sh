#!/bin/bash

# 设置错误时退出
set -e

# 应用名称和端口
APP_NAME="news_web"
PORT=5000
PID_FILE="app.pid"
LOG_FILE="app.log"

# 获取进程ID
get_pid() {
    if [ -f $PID_FILE ]; then
        cat $PID_FILE
    else
        echo ""
    fi
}

# 停止应用
stop_app() {
    echo "停止应用..."
    PID=$(get_pid)
    if [ ! -z "$PID" ]; then
        kill $PID
        rm -f $PID_FILE
        echo "应用已停止"
    else
        echo "应用未运行"
    fi
}

# 启动应用
start_app() {
    echo "启动应用..."
    nohup flask run --host=0.0.0.0 --port=$PORT > $LOG_FILE 2>&1 &
    echo $! > $PID_FILE
    echo "应用已启动，PID: $(get_pid)"
}

echo "开始部署..."

# 拉取最新代码
echo "拉取最新代码..."
git pull

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 清理缓存
echo "清理缓存..."
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# 数据库迁移
echo "执行数据库迁移..."
flask db upgrade

# 初始化数据
echo "初始化数据..."
flask init-data

# 重启应用
stop_app
start_app

echo "部署完成！" 