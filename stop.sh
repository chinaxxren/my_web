#!/bin/bash

# 设置错误时退出
set -e

# 配置文件
PID_FILE="app.pid"
LOG_FILE="logs/app.log"
TIMEOUT=10  # 等待进程停止的超时时间（秒）

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

# 优雅停止
graceful_stop() {
    local pid=$1
    echo "正在尝试优雅停止进程 $pid..."
    kill "$pid" 2>/dev/null || true
    
    # 等待进程停止
    for i in $(seq 1 $TIMEOUT); do
        if ! check_process "$pid"; then
            echo "进程已优雅停止"
            return 0
        fi
        echo "等待进程停止... ($i/$TIMEOUT)"
        sleep 1
    done
    
    return 1
}

# 强制停止
force_stop() {
    local pid=$1
    echo "正在强制停止进程 $pid..."
    kill -9 "$pid" 2>/dev/null || true
    
    # 等待进程停止
    for i in $(seq 1 3); do
        if ! check_process "$pid"; then
            echo "进程已强制停止"
            return 0
        fi
        echo "等待强制停止... ($i/3)"
        sleep 1
    done
    
    return 1
}

# 清理文件
cleanup() {
    local pid=$1
    if [ -f "$PID_FILE" ]; then
        rm -f "$PID_FILE"
        echo "已清理 PID 文件"
    fi
}

# 主停止流程
echo "开始停止服务器..."

# 获取进程ID
pid=$(get_pid)

if [ -z "$pid" ]; then
    echo "错误：未找到 PID 文件"
    exit 1
fi

if ! check_process "$pid"; then
    echo "错误：进程 $pid 不存在"
    cleanup "$pid"
    exit 1
fi

# 尝试优雅停止
if ! graceful_stop "$pid"; then
    echo "优雅停止失败，尝试强制停止..."
    if ! force_stop "$pid"; then
        echo "错误：无法停止进程 $pid"
        exit 1
    fi
fi

# 清理文件
cleanup "$pid"

echo "服务器已成功停止" 