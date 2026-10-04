#!/bin/bash
# 大衍筮法 Docker 快速部署脚本

echo "🌟 大衍筮法 Docker 快速部署"
echo "=============================="

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

echo "✅ Docker检查通过"

# 停止现有容器
echo "🛑 清理现有容器..."
docker stop dayansifa-web 2>/dev/null || true
docker rm dayansifa-web 2>/dev/null || true

# 启动新容器
echo "🚀 启动大衍筮法容器..."
docker run -d \
  --name dayansifa-web \
  --restart unless-stopped \
  -p 8081:8080 \
  -v "$(pwd):/app" \
  -w /app \
  -e PYTHONPATH=/app \
  -e PYTHONUNBUFFERED=1 \
  python:3.9-slim \
  python webserver_v2.py --host=0.0.0.0 --port=8080

if [ $? -eq 0 ]; then
    echo "✅ 容器启动成功"
    
    echo "⏳ 等待服务启动..."
    sleep 10
    
    # 测试服务
    if curl -s http://localhost:8081/api/health > /dev/null; then
        echo "✅ 服务运行正常"
    else
        echo "⚠️ 服务可能还在启动中，请稍后访问"
    fi
    
    echo ""
    echo "🎉 部署完成！"
    echo ""
    echo "📱 Web界面: http://localhost:8081"
    echo "🔗 API健康检查: http://localhost:8081/api/health"
    echo "📊 统计信息: http://localhost:8081/api/stats"
    echo ""
    echo "📚 管理命令:"
    echo "  查看日志: docker logs dayansifa-web"
    echo "  停止服务: docker stop dayansifa-web"
    echo "  重启服务: docker restart dayansifa-web"
    echo ""
else
    echo "❌ 容器启动失败"
    exit 1
fi