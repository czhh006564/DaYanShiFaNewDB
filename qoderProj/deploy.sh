#!/bin/bash
# 大衍筮法程序部署脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
APP_NAME="dayansifa"
IMAGE_NAME="dayansifa/dayansifa"
CONTAINER_NAME="dayansifa-web"
HOST_PORT=${HOST_PORT:-8080}
CONTAINER_PORT=${CONTAINER_PORT:-8080}
ENV=${ENV:-production}

# 函数定义
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_warning "Docker Compose 未安装，某些功能可能不可用"
    fi
    
    log_success "Docker 环境检查通过"
}

build_image() {
    log_info "构建 Docker 镜像..."
    
    docker build -t ${IMAGE_NAME}:latest . \
        --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
        --build-arg VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    
    log_success "Docker 镜像构建完成"
}

stop_container() {
    log_info "停止现有容器..."
    
    if docker ps -q -f name=${CONTAINER_NAME} | grep -q .; then
        docker stop ${CONTAINER_NAME}
        docker rm ${CONTAINER_NAME}
        log_success "已停止并移除现有容器"
    else
        log_info "没有运行中的容器需要停止"
    fi
}

start_container() {
    log_info "启动新容器..."
    
    docker run -d \
        --name ${CONTAINER_NAME} \
        --restart unless-stopped \
        -p ${HOST_PORT}:${CONTAINER_PORT} \
        -e DAYANSIFA_ENV=${ENV} \
        -e DAYANSIFA_WEB_SERVER_HOST=0.0.0.0 \
        -e DAYANSIFA_WEB_SERVER_PORT=${CONTAINER_PORT} \
        -v dayansifa_data:/app/data \
        -v dayansifa_logs:/app/logs \
        -v dayansifa_exports:/app/exports \
        ${IMAGE_NAME}:latest
    
    log_success "容器已启动"
}

check_health() {
    log_info "检查应用健康状态..."
    
    # 等待应用启动
    sleep 10
    
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f http://localhost:${HOST_PORT}/api/health > /dev/null; then
            log_success "应用健康检查通过"
            return 0
        fi
        
        log_info "等待应用启动... (${attempt}/${max_attempts})"
        sleep 2
        ((attempt++))
    done
    
    log_error "应用健康检查失败"
    return 1
}

show_status() {
    echo
    log_info "部署完成！"
    echo "🌟 大衍筮法应用信息:"
    echo "   📱 Web界面: http://localhost:${HOST_PORT}"
    echo "   🔗 API端点: http://localhost:${HOST_PORT}/api/health"
    echo "   📊 统计信息: http://localhost:${HOST_PORT}/api/stats"
    echo "   🐳 容器名称: ${CONTAINER_NAME}"
    echo "   🏷️  镜像标签: ${IMAGE_NAME}:latest"
    echo
    echo "📚 常用命令:"
    echo "   查看日志: docker logs ${CONTAINER_NAME}"
    echo "   进入容器: docker exec -it ${CONTAINER_NAME} bash"
    echo "   停止服务: docker stop ${CONTAINER_NAME}"
    echo "   重启服务: docker restart ${CONTAINER_NAME}"
}

show_usage() {
    echo "大衍筮法部署脚本"
    echo
    echo "用法: $0 [选项] [命令]"
    echo
    echo "命令:"
    echo "  deploy    完整部署 (构建镜像 + 启动容器)"
    echo "  build     仅构建镜像"
    echo "  start     仅启动容器"
    echo "  stop      停止容器"
    echo "  restart   重启容器"
    echo "  status    查看状态"
    echo "  logs      查看日志"
    echo "  clean     清理资源"
    echo
    echo "选项:"
    echo "  -p, --port PORT     指定主机端口 (默认: 8080)"
    echo "  -e, --env ENV       指定环境 (默认: production)"
    echo "  -h, --help          显示帮助信息"
    echo
    echo "环境变量:"
    echo "  HOST_PORT           主机端口"
    echo "  CONTAINER_PORT      容器端口"
    echo "  ENV                 运行环境"
}

deploy() {
    log_info "开始部署大衍筮法应用..."
    
    check_docker
    build_image
    stop_container
    start_container
    
    if check_health; then
        show_status
    else
        log_error "部署失败，请检查日志"
        docker logs ${CONTAINER_NAME}
        exit 1
    fi
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--port)
            HOST_PORT="$2"
            shift 2
            ;;
        -e|--env)
            ENV="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        deploy)
            COMMAND="deploy"
            shift
            ;;
        build)
            COMMAND="build"
            shift
            ;;
        start)
            COMMAND="start"
            shift
            ;;
        stop)
            COMMAND="stop"
            shift
            ;;
        restart)
            COMMAND="restart"
            shift
            ;;
        status)
            COMMAND="status"
            shift
            ;;
        logs)
            COMMAND="logs"
            shift
            ;;
        clean)
            COMMAND="clean"
            shift
            ;;
        *)
            log_error "未知参数: $1"
            show_usage
            exit 1
            ;;
    esac
done

# 执行命令
case ${COMMAND:-deploy} in
    deploy)
        deploy
        ;;
    build)
        check_docker
        build_image
        ;;
    start)
        check_docker
        start_container
        check_health && show_status
        ;;
    stop)
        stop_container
        ;;
    restart)
        stop_container
        start_container
        check_health && show_status
        ;;
    status)
        docker ps -f name=${CONTAINER_NAME}
        if check_health; then
            log_success "应用运行正常"
        fi
        ;;
    logs)
        docker logs -f ${CONTAINER_NAME}
        ;;
    clean)
        log_info "清理资源..."
        docker stop ${CONTAINER_NAME} 2>/dev/null || true
        docker rm ${CONTAINER_NAME} 2>/dev/null || true
        docker rmi ${IMAGE_NAME}:latest 2>/dev/null || true
        docker volume prune -f
        log_success "清理完成"
        ;;
esac