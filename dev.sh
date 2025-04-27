#!/bin/bash

# 设置错误时退出
set -e

# 应用名称和端口
APP_NAME="news_web"
PORT=5000
PID_FILE="dev.pid"
LOG_FILE="dev.log"

# 获取本机IP地址
get_ip() {
    if command -v ip &> /dev/null; then
        ip addr show | grep "inet " | grep -v "127.0.0.1" | awk '{print $2}' | cut -d/ -f1 | head -n 1
    elif command -v ifconfig &> /dev/null; then
        ifconfig | grep "inet " | grep -v "127.0.0.1" | awk '{print $2}' | head -n 1
    else
        echo "无法获取IP地址"
        exit 1
    fi
}

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
    echo "停止开发服务器..."
    PID=$(get_pid)
    if [ ! -z "$PID" ]; then
        kill $PID
        rm -f $PID_FILE
        echo "开发服务器已停止"
    else
        echo "开发服务器未运行"
    fi
}

# 启动应用
start_app() {
    echo "启动开发服务器..."
    # 设置开发环境变量
    export FLASK_APP=app
    export FLASK_ENV=development
    export FLASK_DEBUG=1
    
    # 获取本机IP
    IP=$(get_ip)
    if [ -z "$IP" ]; then
        echo "错误：无法获取本机IP地址"
        exit 1
    fi
    
    # 使用 flask run 启动开发服务器，启用调试模式和自动重载
    nohup flask run --host=0.0.0.0 --port=$PORT --debugger --reload > $LOG_FILE 2>&1 &
    echo $! > $PID_FILE
    echo "开发服务器已启动，PID: $(get_pid)"
    echo "日志文件: $LOG_FILE"
    echo "本地访问地址: http://localhost:$PORT"
    echo "局域网访问地址: http://$IP:$PORT"
    echo "注意：确保防火墙已开放 $PORT 端口"
}

# 显示日志
show_log() {
    if [ -f $LOG_FILE ]; then
        tail -f $LOG_FILE
    else
        echo "日志文件不存在"
    fi
}

# 清理开发环境
clean() {
    echo "清理开发环境..."
    stop_app
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    rm -f $LOG_FILE
    echo "清理完成"
}

# 安装开发依赖
install_dev() {
    echo "安装开发依赖..."
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    echo "开发依赖安装完成"
}

# 显示帮助信息
show_help() {
    echo "开发环境管理脚本"
    echo "用法: ./dev.sh [命令]"
    echo ""
    echo "命令:"
    echo "  start    启动开发服务器"
    echo "  stop     停止开发服务器"
    echo "  restart  重启开发服务器"
    echo "  log      显示日志"
    echo "  clean    清理开发环境"
    echo "  install  安装开发依赖"
    echo "  help     显示帮助信息"
}

# 根据参数执行相应命令
case "$1" in
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        stop_app
        start_app
        ;;
    log)
        show_log
        ;;
    clean)
        clean
        ;;
    install)
        install_dev
        ;;
    help|*)
        show_help
        ;;
esac 