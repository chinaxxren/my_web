#!/bin/bash

# 设置错误时退出
set -e

# 应用名称和端口
APP_NAME="news_web"
PORT=3389
PID_FILE="app.pid"
LOG_FILE="app.log"
LOCK_FILE="deploy.lock"

# 检查是否已经有部署在进行
if [ -f "$LOCK_FILE" ]; then
    echo "错误：另一个部署正在进行中"
    exit 1
fi

# 创建锁文件
touch "$LOCK_FILE"

# 清理函数
cleanup() {
    rm -f "$LOCK_FILE"
    echo "清理完成"
}

# 确保在脚本退出时清理锁文件
trap cleanup EXIT

# 获取进程ID
get_pid() {
    if [ -f "$PID_FILE" ]; then
        cat "$PID_FILE"
    else
        echo ""
    fi
}

# 检查进程是否存在
check_process() {
    local pid=$1
    if [ -z "$pid" ]; then
        return 1
    fi
    if ps -p "$pid" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# 停止应用
stop_app() {
    echo "停止应用..."
    local pid=$(get_pid)
    if [ -n "$pid" ] && check_process "$pid"; then
        echo "正在停止进程 $pid..."
        kill "$pid" || true
        # 等待进程结束
        for i in {1..10}; do
            if ! check_process "$pid"; then
                break
            fi
            sleep 1
        done
        # 如果进程仍然存在，强制终止
        if check_process "$pid"; then
            echo "进程未响应，强制终止..."
            kill -9 "$pid" || true
        fi
        rm -f "$PID_FILE"
        echo "应用已停止"
    else
        echo "应用未运行"
        rm -f "$PID_FILE"
    fi
}

# 启动应用
start_app() {
    echo "启动应用..."
    stop_app  # 确保没有旧进程在运行
    
    # 创建日志目录（如果不存在）
    mkdir -p logs
    
    # 启动应用并记录PID
    nohup flask run --host=0.0.0.0 --port="$PORT" > "logs/$LOG_FILE" 2>&1 &
    local pid=$!
    echo "$pid" > "$PID_FILE"
    
    # 等待应用启动
    for i in {1..10}; do
        if check_process "$pid"; then
            echo "应用已启动，PID: $pid"
            return 0
        fi
        sleep 1
    done
    
    echo "错误：应用启动失败"
    return 1
}

# 主部署流程
echo "开始部署..."

# 拉取最新代码
echo "拉取最新代码..."
git pull || { echo "错误：拉取代码失败"; exit 1; }

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt || { echo "错误：安装依赖失败"; exit 1; }

# 清理缓存
echo "清理缓存..."
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# 数据库迁移
echo "执行数据库迁移..."

# 检查数据库文件是否存在
if [ ! -f "instance/app.db" ]; then
    echo "创建数据库..."
    mkdir -p instance
    touch instance/app.db
fi

# 确保migrations目录存在
if [ ! -d "migrations" ]; then
    echo "初始化数据库迁移..."
    export FLASK_APP=app
    flask db init || { echo "错误：数据库迁移初始化失败"; exit 1; }
fi

# 创建并应用迁移
echo "创建迁移..."
export FLASK_APP=app
flask db migrate -m "Initial migration" || { echo "错误：迁移创建失败"; exit 1; }
echo "应用迁移..."
flask db upgrade || { echo "错误：迁移应用失败"; exit 1; }

# 初始化数据
echo "初始化数据..."
flask init-data || { echo "错误：数据初始化失败"; exit 1; }

# 重启应用
if start_app; then
    echo "部署完成！"
else
    echo "部署失败！"
    exit 1
fi 